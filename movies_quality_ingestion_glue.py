import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsgluedq.transforms import EvaluateDataQuality
from awsglue import DynamicFrame
import concurrent.futures
import re


class GroupFilter:
    def __init__(self, name, filters):
        self.name = name
        self.filters = filters


def apply_group_filter(source_DyF, group):
    return Filter.apply(frame=source_DyF, f=group.filters)


def threadedRoute(glue_ctx, source_DyF, group_filters) -> DynamicFrameCollection:
    dynamic_frames = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_filter = {
            executor.submit(apply_group_filter, source_DyF, gf): gf
            for gf in group_filters
        }
        for future in concurrent.futures.as_completed(future_to_filter):
            gf = future_to_filter[future]
            if future.exception() is not None:
                print("%r generated an exception: %s" % (gf, future.exception()))
            else:
                dynamic_frames[gf.name] = future.result()
    return DynamicFrameCollection(dynamic_frames, glue_ctx)


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="movies-dataset-metadata",
    table_name="imdb_movies_rating_csv",
    transformation_ctx="S3bucket_node1",
)

# Script generated for node Evaluate Data Quality
EvaluateDataQuality_node1693060710028_ruleset = """
    # Example rules: Completeness "colA" between 0.4 and 0.8, ColumnCount > 10
    Rules = [
          RowCount between 500 and 2000,
        IsComplete "poster_link",
        Uniqueness "poster_link" > 0.95,
        ColumnLength "poster_link" between 108 and 162,
        IsComplete "series_title",
        Uniqueness "series_title" > 0.95,
        ColumnLength "series_title" between 1 and 69,
        IsComplete "released_year",
        ColumnValues "released_year" in ["2014","2004","2009","2016","2013","2001","2006","2007","2015","2012","2010","2019","1993","2017","2003","2008","1995","2000","2018","2002","1997","2011","1998","2005","1999","1994","1962","1973","1987","1992","1979","1991","1988","1960","1982","1989","1967","1996","1984","1985","1957","1975","1986","1971","1990","1972","1980","1968","1976","1940","1966","1959","1964","1978","1955","1948","1974","1954","2020","1956","1951","1963","1953","1946","1939","1961","1983","1950","1944","1952","1981","1958","1965","1949","1938","1970","1977","1933","1942","1969","1935","1931","1925","1945","1927","1934","1941","1947","1932","1928","1930","1937","1926","1922","1921","PG","1924","1943","1920","1936"],
        ColumnValues "released_year" in ["2014","2004","2009","2016","2013","2001","2006","2007","2015","2012","2010","2019","1993","2017","2003","2008","1995","2000","2018","2002","1997","2011","1998","2005","1999","1994","1962","1973","1987","1992","1979","1991","1988","1960","1982","1989","1967","1996","1984","1985","1957","1975","1986","1971","1990","1972","1980","1968","1976","1940","1966","1959","1964","1978","1955","1948","1974","1954","2020","1956","1951","1963","1953"] with threshold >= 0.88,
        ColumnLength "released_year" between 1 and 5,
        IsComplete "certificate",
        ColumnValues "certificate" in ["U","A","UA","R","","PG-13","PG"] with threshold >= 0.91,
        ColumnLength "certificate" <= 8,
        IsComplete "runtime",
        ColumnLength "runtime" between 5 and 8,
        IsComplete "genre",
        ColumnLength "genre" between 4 and 30,
        IsComplete "imdb_rating",
        ColumnValues "imdb_rating" between 6.6 and 8,
        IsComplete "overview",
        ColumnLength "overview" between 39 and 314,
        Completeness "meta_score" >= 0.82,
        ColumnValues "meta_score" in ["76","90","84","85","86","80","72","73","81","77","82","83","88","78","74","79","75","87","68","94","91","96","71","66","70","69","65","89","93","67","92","64","97","100","95","62","61"] with threshold >= 0.89,
        StandardDeviation "meta_score" between 11.75 and 12.99,
        ColumnValues "meta_score" between 27 and 101,
        IsComplete "director",
        ColumnLength "director" between 6 and 33,
        IsComplete "star1",
        ColumnLength "star1" between 3 and 26,
        IsComplete "star2",
        ColumnLength "star2" between 3 and 26,
        IsComplete "star3",
        Uniqueness "star3" > 0.6,
        ColumnLength "star3" between 3 and 28,
        IsComplete "star4",
        ColumnLength "star4" between 3 and 28,
        IsComplete "no_of_votes",
        StandardDeviation "no_of_votes" between 310848.53 and 343569.43,
        Uniqueness "no_of_votes" > 0.95,
        ColumnValues "no_of_votes" between 25087 and 2343111,
        IsComplete "gross",
        ColumnLength "gross" <= 11  
    ]
"""

EvaluateDataQuality_node1693060710028 = EvaluateDataQuality().process_rows(
    frame=S3bucket_node1,
    ruleset=EvaluateDataQuality_node1693060710028_ruleset,
    publishing_options={
        "dataQualityEvaluationContext": "EvaluateDataQuality_node1693060710028",
        "enableDataQualityCloudWatchMetrics": True,
        "enableDataQualityResultsPublishing": True,
    },
    additional_options={"performanceTuning.caching": "CACHE_NOTHING"},
)

# Script generated for node rowLevelOutcomes
rowLevelOutcomes_node1693061890331 = SelectFromCollection.apply(
    dfc=EvaluateDataQuality_node1693060710028,
    key="rowLevelOutcomes",
    transformation_ctx="rowLevelOutcomes_node1693061890331",
)

# Script generated for node ruleOutcomes
ruleOutcomes_node1693062294645 = SelectFromCollection.apply(
    dfc=EvaluateDataQuality_node1693060710028,
    key="ruleOutcomes",
    transformation_ctx="ruleOutcomes_node1693062294645",
)

# Script generated for node Conditional Router
ConditionalRouter_node1693062474722 = threadedRoute(
    glueContext,
    source_DyF=rowLevelOutcomes_node1693061890331,
    group_filters=[
        GroupFilter(
            name="output_group_1",
            filters=lambda row: (
                bool(re.match("Failed", row["DataQualityEvaluationResult"]))
            ),
        ),
        GroupFilter(
            name="default_group",
            filters=lambda row: (
                not (bool(re.match("Failed", row["DataQualityEvaluationResult"])))
            ),
        ),
    ],
)

# Script generated for node default_group
default_group_node1693062474769 = SelectFromCollection.apply(
    dfc=ConditionalRouter_node1693062474722,
    key="default_group",
    transformation_ctx="default_group_node1693062474769",
)

# Script generated for node output_group_1
output_group_1_node1693062474770 = SelectFromCollection.apply(
    dfc=ConditionalRouter_node1693062474722,
    key="output_group_1",
    transformation_ctx="output_group_1_node1693062474770",
)

# Script generated for node Change Schema
ChangeSchema_node1693066971682 = ApplyMapping.apply(
    frame=default_group_node1693062474769,
    mappings=[
        ("poster_link", "string", "poster_link", "varchar"),
        ("series_title", "string", "series_title", "varchar"),
        ("released_year", "string", "released_year", "varchar"),
        ("certificate", "string", "certificate", "varchar"),
        ("runtime", "string", "runtime", "varchar"),
        ("genre", "string", "genre", "varchar"),
        ("imdb_rating", "double", "imdb_rating", "decimal"),
        ("overview", "string", "overview", "varchar"),
        ("meta_score", "long", "meta_score", "int"),
        ("director", "string", "director", "varchar"),
        ("star1", "string", "star1", "varchar"),
        ("star2", "string", "star2", "varchar"),
        ("star3", "string", "star3", "varchar"),
        ("star4", "string", "star4", "varchar"),
        ("no_of_votes", "long", "no_of_votes", "int"),
        ("gross", "string", "gross", "varchar"),
    ],
    transformation_ctx="ChangeSchema_node1693066971682",
)

# Script generated for node Amazon S3
AmazonS3_node1693062328577 = glueContext.write_dynamic_frame.from_options(
    frame=ruleOutcomes_node1693062294645,
    connection_type="s3",
    format="json",
    connection_options={
        "path": "s3://movies-dq-results/rule_outcome/",
        "compression": "snappy",
        "partitionKeys": [],
    },
    transformation_ctx="AmazonS3_node1693062328577",
)

# Script generated for node Amazon S3
AmazonS3_node1693062660255 = glueContext.write_dynamic_frame.from_options(
    frame=output_group_1_node1693062474770,
    connection_type="s3",
    format="json",
    connection_options={
        "path": "s3://movies-dq-results/bad_data/",
        "partitionKeys": [],
    },
    transformation_ctx="AmazonS3_node1693062660255",
)

# Script generated for node Amazon Redshift
AmazonRedshift_node1693062707268 = glueContext.write_dynamic_frame.from_options(
    frame=ChangeSchema_node1693066971682,
    connection_type="redshift",
    connection_options={
        "redshiftTmpDir": "s3://aws-glue-assets-348532040329-us-east-1/temporary/",
        "useConnectionProperties": "true",
        "dbtable": "movies.imdb_movies_rating",
        "connectionName": "gds-redshift-connection",
        "preactions": "CREATE TABLE IF NOT EXISTS movies.imdb_movies_rating (poster_link VARCHAR, series_title VARCHAR, released_year VARCHAR, certificate VARCHAR, runtime VARCHAR, genre VARCHAR, imdb_rating DECIMAL, overview VARCHAR, meta_score INTEGER, director VARCHAR, star1 VARCHAR, star2 VARCHAR, star3 VARCHAR, star4 VARCHAR, no_of_votes INTEGER, gross VARCHAR);",
    },
    transformation_ctx="AmazonRedshift_node1693062707268",
)

job.commit()