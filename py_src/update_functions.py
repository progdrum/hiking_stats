from datetime import datetime


def round_to_half(value):
    """
    Round to the nearest half of an integer for easier binning.

    :param value: Value to round
    :return: The rounded value
    """
    return round(value * 2) / 2


def update_distances(records):
    """
    Given updated records, update the distance values for display.

    :param records: Updated trail distance records
    :return: Updated counts and bins
    """
    distance_values = sorted(map(lambda x: round_to_half(x),
                                 [trail['Distance'] for trail in records]))
    distance_bins = list(set(distance_values))
    return [distance_values.count(dist) for dist in distance_bins], distance_bins


def update_stats_box(records):
    """
    Given updated records, update the stats displayed in the stats box for display.

    :param records: The new records to update from (as Pandas DataFrame)
    :return: The updated stats to fill the box in with
    """
    return records.describe().to_string()


def update_line_graphs(records):
    """
    Given updated records, update the stats displayed in the line graphs.

    :param records: Updated trail data records
    :return: Updated data source for use by the line graphs
    """
    distances = [trail['Distance'] for trail in records]
    dates = sorted([datetime.strptime(trail['Date'], '%Y/%m/%d %H:%M')
                    for trail in records])
    energy = [trail['Energy'] for trail in records]
    min_altitude = [trail['Min altitude'] for trail in records]
    max_altitude = [trail['Max altitude'] for trail in records]
    print(len(distances))
    print(len(dates))
    print(len(energy))
    print(len(min_altitude))
    print(len(max_altitude))

    return dict(distances=distances,
                dates=dates,
                energy=energy,
                min_altitude=min_altitude,
                max_altitude=max_altitude)
