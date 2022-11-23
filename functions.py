import os
import pandas as pd
import config

latest_YM=config.latest_YM

def create_df_all(rank_category):
    #print(f'creating df for {rank_category}')
    file_ls=[]
    for dirname, _, filenames in os.walk(f'./datasets/ranking/{rank_category}'):
        for filename in filenames:
            file_ls.append(os.path.join(dirname, filename))
    for i, file in enumerate(file_ls):
        df_tmp=pd.read_csv(file)
        ym_tmp=file.split('_',3)[-1].split('.')[0]
        if ym_tmp[-2]=='_':
            ym_tmp=ym_tmp[:5]+'0'+ym_tmp[-1]
        ym_tmp=ym_tmp.replace('_','-')
        df_tmp['YM']=ym_tmp
        if i==0:
            df_cmp_all=df_tmp
        else:
            df_cmp_all=pd.concat([df_cmp_all,df_tmp])
    df_cmp_all = df_cmp_all.fillna('UNKOWN')
    df_cmp_all.sort_values(by=['rank'],kind='stable',ascending=True,inplace=True)
    df_cmp_all.sort_values(by=['YM'],kind='stable',ascending=False,inplace=True)
    df_cmp_all.reset_index(drop=True, inplace=True)

    url_users=list(set(df_cmp_all.url))
    for url in url_users:
        name_id=df_cmp_all[df_cmp_all['url']==url].name.values[0]+' ('+url.split('/')[-1]+')'
        df_cmp_all.loc[df_cmp_all['url'] ==url, 'name_id'] = name_id

        if df_cmp_all[df_cmp_all['url']==url].YM.values[0]==latest_YM:
            rank_tmp=df_cmp_all[df_cmp_all['url']==url]['rank'].values[0]
        else:
            rank_tmp="1000+"
        rank_name_id="[Rank: "+str(rank_tmp) + "] " +df_cmp_all[df_cmp_all['url']==url].name.values[0]+' ('+url.split('/')[-1]+')'
        df_cmp_all.loc[df_cmp_all['url'] ==url, 'rank_name_id'] = rank_name_id
        df_cmp_all.loc[df_cmp_all['url'] == url, 'latest_rank'] = 1001 if rank_tmp=="1000+" else rank_tmp
    return df_cmp_all


def add_latest_rank_in_country(df):
    df_tmp = df.copy()
    df_out=df.copy()
    df_out['crank_name_id']=float('nan')
    ranked_users_ls = df_tmp[df_tmp['YM'] == latest_YM].name_id

    tmp = "[Rank: " + df_tmp[df_tmp['YM'] == latest_YM].rank()['rank'].astype(int).astype(str) + "] " + \
          df_tmp[df_tmp['YM'] == latest_YM].name_id

    if len(ranked_users_ls) > 0:
        for j, ranked_user in enumerate(ranked_users_ls):
            v = tmp.values[j]
            row_indexer_ls = df_tmp[df_tmp['name_id'] == ranked_user].index.tolist()
            df_tmp.loc[row_indexer_ls, 'crank_name_id'] = v
            df_tmp.loc[row_indexer_ls, 'crank'] = v.split(' ',2)[1][:-1]
        df_out.loc[df_tmp.crank_name_id.index.tolist(), 'crank_name_id'] = df_tmp.crank_name_id.values
        df_out.loc[df_tmp.crank_name_id.index.tolist(), 'crank'] = df_tmp.crank.values

    tmp_df = df_out[df_out.crank_name_id.isna()].copy()
    df_out.loc[tmp_df.index, 'crank_name_id'] = "[WR1000+ or moved] " + tmp_df.name_id.values
    df_out.loc[tmp_df.index, 'crank'] = "WR1000+ or moved"
    return df_out