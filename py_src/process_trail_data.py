import json
import pandas as pd
import pymongo as pm


class HikingProcess(object):
    default_path = '~/Documents/datasets/hiking_data/hiking_stats.csv'

    def read_and_process_csv(self, path=default_path):
        """
        Read CSV data and split into solo and group hikes for further processing.

        :param path: THe path to the CSV file to read from
        :return: A tuple containing Pandas dataframes of all the data, solo data only,
                 and group data only
        """
        # Basic read-in of data
        hiking_data = pd.read_csv(path)

        # Split between solo and group hikes (Re-do this with dplython or something?)
        solo_hikes = hiking_data.loc[hiking_data.loc[:, 'Solo'] == True, :]
        group_hikes = hiking_data.loc[hiking_data.loc[:, 'Solo'] == False, :]

        return hiking_data, solo_hikes, group_hikes

    def read_and_store_mongo(self, csv_path=default_path):
        """
        Read CSV data and store in Mongo DB.

        :param csv_path: The path to the CSV file to read from.
        :return: Nothing
        """
        # Associate the client, DB, and collection
        client = pm.MongoClient("localhost", 27017)
        db = client["trail_data"]
        collection = db["stats"]

        # Load the CSV data and convert to JSON format
        csv_data = pd.read_csv(csv_path)
        json_data = json.loads(csv_data.to_json(orient="records"))

        # Perform the upsert operation
        for trail in json_data:
            collection.update_one({'Park/Trail': trail['Park/Trail']},
                                  {'$set': {
                                      'After Work': trail['After Work'],
                                      'Avg moving speed': trail['Avg. moving speed'],
                                      'Avg speed': trail['Avg. speed'],
                                      'Date': trail['Date'],
                                      'Distance': trail['Distance'],
                                      'Distance (Downhill)': trail['Distance (Downhill)'],
                                      'Distance (Uphill)': trail['Distance (Uphill)'],
                                      'Elevation (Downhill)': trail['Elevation (Downhill)'],
                                      'Elevation (Uphill)': trail['Elevation (Uphill)'],
                                      'Energy': trail['Energy'],
                                      'Max altitude': trail['Max. altitude'],
                                      'Max speed': trail['Max. speed'],
                                      'Min altitude': trail['Min. altitude'],
                                      'Pace': trail['Pace'],
                                      'Park system': trail['Park system'],
                                      'Park/Trail': trail['Park/Trail'],
                                      'Solo': trail['Solo'],
                                      'Track time': trail['Track time'],
                                      'Track time (Movement)': trail['Track time (Movement)']
                                  }},
                                  upsert=True)
