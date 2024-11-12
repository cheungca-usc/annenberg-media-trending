from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import pandas as pd

def sample_run_report(property_id="YOUR-GA4-PROPERTY-ID"):
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.
    property_id = "385998900"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(

        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePathPlusQueryString"), Dimension(name="pageTitle"),
                    Dimension(name="fullPageUrl"), Dimension(name="nthday")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],

    )
    response = client.run_report(request)

    # creating a dataframe
    print("Top Articles:")
    data = [
        (row.dimension_values[0].value,  # path
         row.dimension_values[2].value,  # url
         row.metric_values[0].value,  # views
         row.dimension_values[3].value, # date
         row.dimension_values[1].value.replace(' – Annenberg Media', ''))  # title
        for row in response.rows
    ]
    views_df = pd.DataFrame(data, columns=['path', 'url', 'views', 'days_since_start', 'title'])
    views_df = views_df.astype({'days_since_start': 'int64', 'views': 'int64'})

    # filter for articles
    views_df = views_df[views_df['path'].str.contains(r"^/\d{4}/\d{2}/\d{2}", regex=True)]
    # weight the view counts by recency
    views_df = views_df.groupby(['url', 'title', 'days_since_start']).sum().reset_index()
    views_df['weighted_score'] = views_df['views'] * (5**(views_df['days_since_start']))
    # total the weighted view counts
    views_df = views_df.groupby(['url', 'title'])[['views', 'weighted_score']].sum().reset_index()
    # display articles with the 5 highest total weighted view count
    top_pages = views_df.sort_values(by='weighted_score', ascending=False).head(5)
    print(top_pages)

    # writing the top_pages to data.js
    json_data = top_pages.to_json(orient='records')
    with open('data.js', 'w') as f:
        f.write('const data = ' + json_data + ';')


if __name__ == '__main__':
    sample_run_report()
