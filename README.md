# AWS Glue ETL Data Quality Pipeline for IMDB Movies Dataset

This repository contains a comprehensive, production-grade **ETL (Extract, Transform, Load)** pipeline built with **AWS Glue** and **Amazon Redshift**. The pipeline processes a raw IMDb movie dataset stored in **Amazon S3**, applies **data quality validation**, dynamically routes data based on validation results, and loads it into **Amazon Redshift** for advanced analytics. Additional integrations with **Amazon EventBridge** and **Amazon SNS** enable event-driven notifications for job status updates.


## What Does This Project Do?

The project automates the ingestion, validation, transformation, and loading of a movie dataset from IMDb. Here's what it accomplishes:  
1. Validates data quality using AWS Glue **Data Quality Rules**.  
2. Transforms valid records into Redshift-compatible schema using **AWS Glue Low-Code ETL**.  
3. Dynamically routes invalid records to **S3** for manual review.  
4. Stores metadata and rules in the **AWS Glue Data Catalog**.  
5. Triggers events and sends notifications via **EventBridge** and **SNS** for job monitoring.  
6. Scales efficiently with multi-threading and distributed cloud infrastructure.  


## Key Features  

1. **Input Source**:  
   - Movie dataset fetched from **Amazon S3** in CSV format.  

2. **Data Quality Evaluation**:  
   - Rules applied for completeness, uniqueness, and range validation for key fields like `poster_link`, `series_title`, and `IMDB_rating`.  
3. **Dynamic Data Routing**:  
   - **Valid Data**: Transformed and sent to Redshift.  
   - **Invalid Data**: Stored in S3 for further review.  

4. **Multi-Threading for Performance**:  
   - Concurrent processing achieved with Python’s `concurrent.futures`.  

5. **Data Quality Metrics**:  
   - Integrated with **AWS Glue EvaluateDataQuality** for rule-based validation.  

6. **Output Targets**:  
   - Validated data in **Amazon Redshift**.  
   - Invalid rows and rule evaluation logs in **Amazon S3**.

## AWS Features Used

| **Feature**                    | **Description**                                                                                       |  
|---------------------------------|-------------------------------------------------------------------------------------------------------|  
| **S3 Integration**              | Stores raw input data, invalid records, and processed outputs.                                        |  
| **Glue Crawler**                | Automatically identifies the schema of the input dataset and updates the Glue Data Catalog.           |  
| **Glue Data Catalog**           | Centralized metadata management for the dataset.                                                      |  
| **Glue Data Quality**           | Ensures data integrity by applying configurable validation rules.                                     |  
| **Glue Low-Code ETL**           | Simplifies ETL transformations with an easy-to-maintain Python script.                               |  
| **Amazon Redshift**             | Stores the final validated and transformed data for analysis.                                         |  
| **Amazon EventBridge**          | Monitors job statuses and triggers notifications for success or failure.                              |  
| **Amazon SNS**                  | Sends email or SMS notifications based on EventBridge triggers.                                       |  



## **Architecture**  

```plaintext  
[S3: Raw IMDb Dataset]  
       ↓  
[Glue Crawler → Glue Catalog]  
       ↓  
[Glue ETL Job]  
       ↓  
+---------------------------+  
| Data Quality Validation  |  
+---------------------------+  
       ↓  
+-------------------+     +----------------+  
| Invalid Records   |     | Valid Records  |  
| (S3/JSON Format)  |     | (Redshift)     |  
+-------------------+     +----------------+  
       ↓                    ↓  
[EventBridge → SNS]       [Redshift Analytics]  
```  


 ### Workflow Overview ###

1. **Data Ingestion**
   - The pipeline ingests a dataset of IMDB movie metadata from an **AWS S3** bucket using the `from_catalog()` method in AWS Glue.

2. **Data Quality Evaluation**
   - The dataset undergoes comprehensive data quality checks using AWS Glue's **EvaluateDataQuality** transform.
   - Example rules include:
     - **Completeness:** Ensures critical columns (e.g., `poster_link`, `series_title`) are fully populated.
     - **Uniqueness:** Validates that values in specific fields are distinct (e.g., `series_title`).
     - **Column Length:** Ensures string fields fall within acceptable length ranges.
     - **Column Value Validation:** Checks that column values belong to expected ranges or categories (e.g., `released_year`).
     - **Statistical Validation:** Validates standard deviation and other statistical properties for numeric columns.

3. **Routing Results**
   - Based on the data quality evaluation:
     - Records failing quality checks are routed to an `output_group_1` collection.
     - Valid records are routed to a `default_group` collection.

4. **Schema Transformation**
   - The valid dataset undergoes schema transformation using `ApplyMapping`:
     - Maps data to appropriate types (e.g., `IMDB_Rating` as `DECIMAL`, `Meta_score` as `INTEGER`).
     - Ensures compatibility with the target Redshift schema.

5. **Data Storage**
   - **S3 Outputs:**
     - Failed records are saved in `s3://movies-dq-results/bad_data/`.
     - Data quality rule outcomes are stored in `s3://movies-dq-results/rule_outcome/`.
   - **Redshift Storage:**
     - Transformed and validated data is stored in the Redshift table `movies.imdb_movies_rating`.



## **Core Schema Details**  

The Redshift table schema is as follows:

| Column Name      | Data Type       | Description                                             |
|------------------|-----------------|---------------------------------------------------------|
| Poster_Link      | VARCHAR(MAX)    | URL to the movie poster image.                         |
| Series_Title     | VARCHAR(MAX)    | Title of the movie or series.                          |
| Released_Year    | VARCHAR(10)     | Year the movie was released.                           |
| Certificate      | VARCHAR(50)     | Age certification of the movie (e.g., U, A, PG-13).    |
| Runtime          | VARCHAR(50)     | Duration of the movie (e.g., 120 mins).                |
| Genre            | VARCHAR(200)    | Genre(s) of the movie (e.g., Action, Drama).           |
| IMDB_Rating      | DECIMAL(10,2)   | IMDB rating of the movie.                              |
| Overview         | VARCHAR(MAX)    | Brief summary or description of the movie.             |
| Meta_score       | INT             | Metacritic score of the movie.                         |
| Director         | VARCHAR(200)    | Name of the movie's director.                          |
| Star1            | VARCHAR(200)    | Name of the first lead actor/actress.                  |
| Star2            | VARCHAR(200)    | Name of the second lead actor/actress.                 |
| Star3            | VARCHAR(200)    | Name of the third lead actor/actress.                  |
| Star4            | VARCHAR(200)    | Name of the fourth lead actor/actress.                 |
| No_of_Votes      | INT             | Number of votes the movie received on IMDB.            |
| Gross            | VARCHAR(20)     | Box office gross revenue of the movie.                 |




## **Data Quality Rules**  

| **Rule**           | **Validation**                                 | **Applied On**     |  
|---------------------|-----------------------------------------------|--------------------|  
| Completeness        | Column must not contain null values.          | `poster_link`      |  
| Uniqueness          | Column values must be unique (>95%).          | `series_title`     |  
| Range Validation    | Column value must be within valid range.       | `IMDB_rating`      |  
| Format Validation   | Checks proper format for fields like `runtime`. | `runtime`          |  



## **Setup Instructions**  

### **Prerequisites**  

1. **AWS Services**:  
   - **S3**: Create a bucket for storing raw, invalid, and processed data.  
   - **Glue**: Set up a Glue database (`movies-dataset-metadata`) and crawler.  
   - **Redshift**: Create a cluster and database schema.  
   - **EventBridge and SNS**: Configure event rules and notifications.  

2. **Tools**:  
   - **AWS CLI**: Configure credentials and region.  
   - **Python 3.7+**: Install required libraries.  



### **Steps to Use**  

1. **Clone the Repository**:  
   ```bash  
   git clone https://github.com/your-username/Movie-Dataset-ETL-Pipeline.git  
   cd Movie-Dataset-ETL-Pipeline  
   ```  

2. **Install Dependencies**:  
   ```bash  
   pip install -r requirements.txt  
   ```  

3. **Configure AWS Resources**:  
   - Upload your raw IMDb dataset to an S3 bucket.  
   - Create a Glue Crawler to discover and update the schema in the Glue Data Catalog.  
   - Create a Redshift table using the schema below:  
     ```sql  
     CREATE TABLE movies.imdb_movies_rating (  
         Poster_Link VARCHAR(MAX),  
         Series_Title VARCHAR(MAX),  
         Certificate VARCHAR(50),
         Runtime VARCHAR(50),
         Genre VARCHAR(200),
         IMDB_Rating DECIMAL(10,2),
         Overview VARCHAR(MAX),
         Meta_score INT,
         Director VARCHAR(200),
         Star1 VARCHAR(200),
         Star2 VARCHAR(200),
         Star3 VARCHAR(200),
         Star4 VARCHAR(200),
         No_of_Votes INT,
         Gross VARCHAR(20) 
     );
     ```  

4. **Run the ETL Job**:  
   - Upload the `main.py` script to AWS Glue.  
   - Execute the Glue job with required parameters (e.g., S3 paths, Redshift connection).  

5. **Monitor and Notifications**:  
   - Use **EventBridge** to monitor job completion or failure.  
   - Receive notifications via **SNS** for alerts.  



## **Output**  

1. **Amazon Redshift**:  
   - Contains validated and transformed IMDb movie data.  

2. **Amazon S3**:  
   - Stores invalid records and detailed logs for debugging.  

3. **EventBridge + SNS**:  
   - Sends job status updates via email or SMS.  



## **Results**  

| **Category**        | **Output**                              |  
|----------------------|-----------------------------------------|  
| Valid Data          | Stored in Redshift for analytics.       |  
| Invalid Records     | Written to S3 in JSON format.           |  
| Rule Evaluation Logs| Stored in S3 for monitoring.            |  
| Notifications       | Sent via SNS for job completion/failure.|  


## **Future Enhancements**

1. **Integration with AWS QuickSight:**
   - Use **QuickSight** for interactive visualizations and dashboards to analyze trends in the IMDB Movies dataset.

2. **Data Lake Integration:**
   - Extend the pipeline to store validated data in an **AWS Lake Formation** data lake.

3. **Real-Time Processing:**
   - Introduce AWS **Kinesis Data Streams** for processing streaming movie metadata.

4. **Advanced Quality Metrics:**
   - Implement advanced data profiling and anomaly detection with machine learning models.



## Contributing

Contributions are welcome! Please open an issue or submit a pull request.


