import pandas as pd


def calculate_pace(df: pd.DataFrame):
    print("Calculating average pace")
    df['pace_in_mins'] = df.apply(lambda x: 1 / ((x['average_speed'] / 1000) * 60), axis=1)
    df['pace_seconds'] = df['pace_in_mins'].apply(lambda x: int(60 * (x - int(x))))  # get seconds
    df['pace_seconds_str'] = df['pace_seconds'].apply(lambda x: f"0{x}" if x < 10 else x)  # get seconds
    df['pace_min'] = df['pace_in_mins'].apply(lambda x: int(x))  # get seconds
    df['pace_min_per_km'] = df.apply(lambda x: f"{x['pace_min']}:{x['pace_seconds_str']}", axis=1)  # get seconds
    return df


def process_activities(activities: dict) -> dict:
    """
        Transform activities to dataframe and perform some calculation
    Parameters
    ----------
    activities

    Returns
    -------
        Dict with list of activities
    """
    # temporaly to avoid requesting a lot
    import json
    # activities = None
    # with open('data.json') as json_file:
    #    activities = json.load(json_file)
    #
    # for activity in activities:
    pd.set_option('display.max_columns', None)
    activities_df = pd.DataFrame.from_dict(data=activities)
    print("Filtering Run main activities")
    run_df = activities_df[activities_df['sport_type'] == 'Run']  # filter run trainings
    training_df = run_df[
        ~run_df['name'].str.contains("Run")]  # not contains Run in name to discard not important trainings
    training_df['type'] = training_df['name'].apply(lambda x: "Training" if str(x).find('Carrera') < 0 else "Race")
    # To construct avg pace
    training_df_pace = calculate_pace(training_df)
    training_df_pace = training_df_pace[
        ['id', 'name', 'type', 'start_date_local', 'distance', 'moving_time', 'average_heartrate', 'max_heartrate',
         'average_speed', 'pace_min_per_km', 'pace_in_mins']]

    print(training_df_pace[0:10])
    return training_df_pace.to_dict("records")


if __name__ == '__main__':
    import json
    with open('../respuesta_activities.json') as f:
        data = json.load(f)
    process_activities(data)
