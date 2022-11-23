from functions import create_df_all
import datetime
import config

def main():
    print('''
    Before run this script, make sure you've downloaded latest ranking datasets from https://www.kaggle.com/datasets/hdsk38/comp-top-1000-data.
    Also, change the latest_YM variable in config.py (e.g., latest_YM = latest_YM='2022-11').
    ''')

    print('competitions')
    print(datetime.datetime.now())
    df_cmp_all = create_df_all('competitions')

    print('datasets')
    print(datetime.datetime.now())
    df_datasets_all = create_df_all('datasets')

    print('notebooks')
    print(datetime.datetime.now())
    df_notebooks_all = create_df_all('notebooks')

    print('discussion')
    print(datetime.datetime.now())
    df_discussion_all = create_df_all('discussion')
    print(datetime.datetime.now())

    df_cmp_all.to_csv(f'./datasets/merged_ranking/competitions/df_cmp_all.csv', index=False)
    df_datasets_all.to_csv(f'./datasets/merged_ranking/datasets/df_datasets_all.csv', index=False)
    df_notebooks_all.to_csv(f'./datasets/merged_ranking/notebooks/df_notebooks_all.csv', index=False)
    df_discussion_all.to_csv(f'./datasets/merged_ranking/discussion/df_discussion_all.csv', index=False)


    print('Checking if countries are covered')
    countries=[]
    countries.extend(df_cmp_all['country'].unique().tolist())
    countries.extend(df_datasets_all['country'].unique().tolist())
    countries.extend(df_notebooks_all['country'].unique().tolist())
    countries.extend(df_discussion_all['country'].unique().tolist())
    countries=set(countries)

    config_countires=[]
    config_countires.extend(config.searchable_countries['options_asia'])
    config_countires.extend(config.searchable_countries['options_oceania'])
    config_countires.extend(config.searchable_countries['options_africa'])
    config_countires.extend(config.searchable_countries['options_europe'])
    config_countires.extend(config.searchable_countries['options_americas'])
    config_countires.append('UNKOWN')
    config_countries=set(config_countires)

    if countries==config_countries:
        print('Countries in config.py is all covered.')
    else:
        print(f'{str(countries-config_countries)} is misssing. Add the countires in config.py.')

if __name__ == '__main__':
    main()