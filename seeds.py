import os
import sys

import pandas as pd
from faunadb import errors
from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.objects import Ref


def createDB():
    admin_secret = os.getenv("ADMIN_SECRET")
    print(admin_secret)
    if not admin_secret:
        print("Please set the ADMIN_SECRET environment variable")
        sys.exit(1)

    try:
        adminClient = FaunaClient(secret=admin_secret)
        print(adminClient)
        db_ref = adminClient.query(q.create_database({"name": "events_paris_2024"}))
        print(db_ref)
        result = adminClient.query(q.paginate(q.databases()))
        print(result)
        skey = adminClient.query(
            q.create_key(
                {
                    "database": q.database("events_paris_2024"),
                    "role": "server",
                }
            )
        )

        with open(".env", "a") as f:
            f.write(f"\nSERVER_SECRET={skey['secret']}\n")
    except errors.FaunaError as e:
        print(f"FaunaDB error: {e}")


def seed():

    server_secret = os.getenv("EVENTS_SECRET")

    # Connect to FaunaDB
    client = FaunaClient(secret=server_secret)

    # r1 = client.query(q.create_collection({"name": "Events"}))
    # print(r1)

    # r2 = client.query(
    #     q.create_index(
    #         {
    #             "name": "Events_by_date",
    #             "source": q.collection("Events"),
    #             "terms": [{"field": ["data", "date"]}],
    #         }
    #     )
    # )
    # print(r2)

    # Read the CSV file
    df = pd.read_csv("./paris-olympics-2024-events.csv")
    df["Additional details"] = df["Additional details"].fillna("No additional details")
    df["Location"] = df["Location"].fillna("No location")
    df["Start time"] = df["Start time"].fillna("No start time")
    df["End time"] = df["End time"].fillna("No end time")

    df["Start time"] = df["Start time"].apply(
        lambda x: (
            str(pd.to_datetime(x).time())
            if pd.to_datetime(x, errors="coerce") is not pd.NaT
            else x
        )
    )
    df["End time"] = df["End time"].apply(
        lambda x: (
            str(pd.to_datetime(x).time())
            if pd.to_datetime(x, errors="coerce") is not pd.NaT
            else x
        )
    )
    df["Date"] = df["Date"].apply(
        lambda x: (
            str(pd.to_datetime(x).date())
            if pd.to_datetime(x, errors="coerce") is not pd.NaT
            else x
        )
    )
    # Iterate over the rows and create documents
    for index, row in df.iterrows():
        # Create a document with the data from the row
        # document = {
        #     "ref": Ref(Collection("olympic_events_2024"), row.name),
        #     "data": {
        #         "date": row["Date"],
        #         "sport": row["Sport"],
        #         "event": row["Event"],
        #         "details": row["Additional Details"],
        #         "start": row["Start time"],
        #         "end": row["End time"],
        #         # Add more fields as needed
        #     },
        # }

        # Create the document in FaunaDB
        # result = client.query(Create(Document(document["ref"]), document["data"]))
        # import ipdb

        # ipdb.set_trace()
        r3 = client.query(
            q.create(
                q.ref(q.collection("Events"), row.name),
                {
                    "data": {
                        "date": row["Date"],
                        "sport": row["Sport"],
                        "event": row["Event"],
                        "details": row["Additional details"],
                        "location": row["Location"],
                        "start": row["Start time"],
                        "end": row["End time"],
                        # Add more fields as needed
                    }
                },
            )
        )

        # Print the result
        print(r3)


if __name__ == "__main__":
    # createDB()
    seed()
