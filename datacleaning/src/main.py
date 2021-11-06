import csv
import datetime
import numpy as np
import re
import datetime
import pandas as pd

def convert_bool(df,list):
    '''
    Takes a list of strings that are column headers, iterates through them and converts it to bool.
    '''

    for each in list:
        df[each].replace({"Yes": True, "Y": True, "No": False, "N": False}, inplace=True)

    return None

def convert_time(df,list):
    '''
    Takes a list of strings that are column headers, iterates through them and converts it to timestamp.
    '''

    for each in list:
        df[each] = pd.to_datetime(df[each],utc=True)

    return None

def typecorrection(List):
    df1 = pd.read_csv(List[0])
    df2 = pd.read_csv(List[1])
    df3 = pd.read_csv(List[2])

    to_bool1 = ["officer_on_duty","officer_injured", "officer_in_uniform", "subject_armed", "subject_injured",
                       "subject_alleged_injury","notify_oemc","notify_district_sergeant","notify_op_command",
                       "notify_det_division"]
    to_bool2 = ['firearm_reloaded', 'sight_used']

    to_timestamp1 = ['trr_datetime', 'trr_created']
    to_timestamp3 = ['status_datetime']

    convert_bool(df1,to_bool1)
    convert_bool(df2,to_bool2)

    convert_time(df1,to_timestamp1)
    convert_time(df3,to_timestamp3)

    df1.to_csv('csv/after_typecorrection/postgres_public_trr_trr_refresh.csv')
    df2.to_csv('csv/after_typecorrection/postgres_public_trr_weapondischarge_refresh.csv')
    df3.to_csv('csv/after_typecorrection/postgres_public_trr_trrstatus_refresh.csv')

def reconciliation(List):
    df = pd.read_csv(List[0])

    def p(x):
      print(df[x].unique())
      print(df[x].isna().sum())

    for x in df['officer_first_name']:
      y=x.split(" ")[0].capitalize()
      df['officer_first_name'] = df['officer_first_name'].replace([x],y)

    for x in df['officer_last_name']:
      y=x.split(" ")[0].capitalize()
      df['officer_last_name'] = df['officer_last_name'].replace([x],y)

    for x in df['officer_birth_year']:
      if not np.isnan(x):
        df['officer_last_name'] = df['officer_last_name'].replace([x], int(x))

    for x in df['officer_race']:
      if x=='UNKNOWN':
        df['officer_race'] = df['officer_race'].replace([x], np.nan)
      if x=='AMER IND/ALASKAN NATIVE':
        df['officer_race'] = df['officer_race'].replace([x], 'NATIVE AMERICAN/ALASKAN NATIVE')

    for x in df['subject_race']:
      if x=='UNKNOWN':
        df['subject_race'] = df['subject_race'].replace([x], np.nan)
      if x=='UNKNOWN / REFUSED':
        df['subject_race'] = df['subject_race'].replace([x], np.nan)
      if x=='AMER IND/ALASKAN NATIVE':
        df['subject_race'] = df['subject_race'].replace([x], 'NATIVE AMERICAN/ALASKAN NATIVE')
      if x=='AMER INDIAN / ALASKAN NATIVE':
        df['subject_race'] = df['subject_race'].replace([x], 'NATIVE AMERICAN/ALASKAN NATIVE')
      if x=='ASIAN / PACIFIC ISLANDER':
        df['subject_race'] = df['subject_race'].replace([x], 'ASIAN/PACIFIC ISLANDER')

    #pd=pd.to_numeric(df['subject_gender'], errors='coerce')
    for x in df['subject_gender']:
      if x=='MALE':
        df['subject_gender'] = df['subject_gender'].replace([x], 'M')
      if x=='FEMALE':
        df['subject_gender'] = df['subject_gender'].replace([x], 'F')

    p('officer_appointed_date')
    for x in df['officer_appointed_date']:
        if x != 'REDACTED':
            print(x)
            if x.split("-")[1].isnumeric() and len(str(x.split("-")[0]))!=4:
                d=datetime.datetime.strptime(x,"%m-%d-%y")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year)+'-'+str(d.month)+'-'+str(d.day)))
            elif x.split("-")[1].isnumeric() and len(str(x.split("-")[0]))==4:
                d=datetime.datetime.strptime(x,"%Y-%m-%d")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year)+'-'+str(d.month)+'-'+str(d.day)))
            elif not x.split("-")[1].isnumeric():
                d = datetime.datetime.strptime(x, "%Y-%b-%d")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year)+'-'+str(d.month)+'-'+str(d.day)))
    for x in df['officer_appointed_date']:
        if x != 'REDACTED':
            if int(x.split("-")[0])>2021:
                d = datetime.datetime.strptime(x, "%Y-%m-%d")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year-100)+'-'+str(d.month)+'-'+str(d.day)))
    p('subject_birth_year')
    for x in df['subject_birth_year']:
        if len(str(x))==2:
            if x>5 and x<100:
                y=int('19'+str(x))
            df['subject_birth_year'] = df['subject_birth_year'].replace([int(x)], int(y))
        if len(str(x))==1:
            x='0'+str(x)
            d = datetime.datetime.strptime(x, "%y")
            df['subject_birth_year'] = df['subject_birth_year'].replace([int(x)],int(d.year))
        if len(str(x))==3:
            y='1'+str(x)
            df['subject_birth_year'] = df['subject_birth_year'].replace([int(x)],int(y))

    p('indoor_or_outdoor')
    for x in df['indoor_or_outdoor']:
        if x=='OUTDOOR':
            df['indoor_or_outdoor'] = df['indoor_or_outdoor'].replace([x], 'Outdoor')
        if x=='INDOOR':
            df['indoor_or_outdoor'] = df['indoor_or_outdoor'].replace([x], 'Indoor')
    p('indoor_or_outdoor')

    df.to_csv('csv/after_recon/postgres_public_trr_trr_refresh.csv')

    df = pd.read_csv(List[1])
    
    for x in df['officer_first_name']:
      y=x.split(" ")[0].capitalize()
      df['officer_first_name'] = df['officer_first_name'].replace([x],y)

    for x in df['officer_last_name']:
      y=x.split(" ")[0].capitalize()
      df['officer_last_name'] = df['officer_last_name'].replace([x],y)

    for x in df['officer_birth_year']:
      if not np.isnan(x):
        df['officer_birth_year'] = df['officer_birth_year'].replace([x], int(x))

    for x in df['officer_race']:
      if x=='UNKNOWN':
        df['officer_race'] = df['officer_race'].replace([x], np.nan)
      if x=='AMER IND/ALASKAN NATIVE':
        df['officer_race'] = df['officer_race'].replace([x], 'NATIVE AMERICAN/ALASKAN NATIVE')

    for x in df['officer_gender']:
      if x=='MALE':
        df['officer_gender'] = df['officer_gender'].replace([x], 'M')
      if x=='FEMALE':
        df['officer_gender'] = df['officer_gender'].replace([x], 'F')

    for x in df['officer_appointed_date']:
        if x!='REDACTED':
            if x.split("-")[1].isnumeric() and len(str(x.split("-")[0]))!=4:
                d=datetime.datetime.strptime(x,"%m-%d-%y")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year)+'-'+str(d.month)+'-'+str(d.day)))
            elif x.split("-")[1].isnumeric() and len(str(x.split("-")[0]))==4:
                d=datetime.datetime.strptime(x,"%Y-%m-%d")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year)+'-'+str(d.month)+'-'+str(d.day)))
            elif not x.split("-")[1].isnumeric():
                d = datetime.datetime.strptime(x, "%Y-%b-%d")
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year)+'-'+str(d.month)+'-'+str(d.day)))

    for x in df['officer_appointed_date']:
        if x!='REDACTED':
            if int(x.split("-")[0])>2021:
                d = datetime.datetime.strptime(x, "%Y-%m-%d")
                print(1)
                print(x,str(d.year-100)+'-'+str(d.month)+'-'+str(d.day))
                df['officer_appointed_date'] = df['officer_appointed_date'].replace([x], (str(d.year-100)+'-'+str(d.month)+'-'+str(d.day)))

    df.to_csv('csv/after_recon/postgres_public_trr_trrstatus_refresh.csv')

def redact(List):

    df1 = pd.read_csv(List[0])
    df2 = pd.read_csv(List[1])
    df3 = pd.read_csv(List[2])

    to_null1 = ['trr_datetime', 'beat', 'officer_appointed_date', 'officer_birth_year', 'officer_age',
                'officer_on_duty',
                'officer_injured', 'officer_in_uniform', 'subject_birth_year', 'subject_age', 'subject_armed',
                'subject_injured',
                'subject_alleged_injury', 'notify_oemc', 'notify_district_sergeant', 'notify_op_command',
                'notify_det_division',
                'trr_created']
    to_null2 = ['firearm_reloaded', 'sight_used']
    to_null3 = ['officer_appointed_date', 'officer_birth_year', 'status_datetime']

    for each in to_null1:
        df1[each].replace({"REDACTED": None}, inplace=True)

    for each in to_null2:
        df2[each].replace({"REDACTED": None}, inplace=True)

    for each in to_null3:
        df3[each].replace({"REDACTED": None}, inplace=True)

    df1.to_csv('csv/after_redact/postgres_public_trr_trr_refresh.csv')
    df2.to_csv('csv/after_redact/postgres_public_trr_weapondischarge_refresh.csv')
    df3.to_csv('csv/after_redact/postgres_public_trr_trrstatus_refresh.csv')

def integration(List):
    trr_df = pd.read_csv(List[0])
    officer_df = pd.read_csv(List[1])
    trr_status_df = pd.read_csv(List[2])

    trr_df.rename(columns={'officer_last_name' : 'last_name','officer_first_name' : 'first_name', 'officer_middle_initial' : 'middle_initial',
                           'officer_appointed_date' : 'appointed_date'},inplace=True)

    trr_status_df.rename(columns={'officer_last_name' : 'last_name','officer_first_name' : 'first_name', 'officer_middle_initial' : 'middle_initial',
                           'officer_appointed_date' : 'appointed_date'},inplace=True)

    match_on = ['last_name', 'first_name', 'appointed_date']

    id = 'id'
    count = 0
    
   for row in sorted(trr_df.index):
        if row % 100 == 0:
            print(f'On row {row}')
        trr_first_name = trr_df.loc[row]['first_name']
        trr_last_name = trr_df.loc[row]['last_name']
        trr_appointed_date = trr_df.loc[row]['appointed_date']
        officer_rows = officer_df.loc[(officer_df['first_name']==trr_first_name) & (officer_df['last_name']==trr_last_name) & (officer_df['appointed_date']==trr_appointed_date)]
        #officer_rows = officer_df.query(f'first_name={trr_first_name} and last_name={trr_last_name} and appointed_date={trr_appointed_date}')
        #if officer_rows.shape[1] > 0:
        #print(officer_rows.shape[0])
        try:#if officer_rows.shape[0] > 0:
            trr_df.loc[row]['first_name'] = officer_rows[0]['first_name']
            trr_df.loc[row]['last_name'] = officer_rows[0]['last_name']
            trr_df.loc[row]['appointed_date'] = officer_rows[0]['appointed_date']
            continue
        except Exception:
            pass

        officer_rows = officer_df.loc[((officer_df['first_name']==trr_first_name) & (officer_df['last_name']==trr_last_name)) | ((officer_df['first_name']==trr_first_name) & (officer_df['appointed_date']==trr_appointed_date)) | ((officer_df['last_name']==trr_last_name) & (officer_df['appointed_date']==trr_appointed_date))]
        try:  # if officer_rows.shape[0] > 0:
            trr_df.loc[row]['first_name'] = officer_rows[0]['first_name']
            trr_df.loc[row]['last_name'] = officer_rows[0]['last_name']
            trr_df.loc[row]['appointed_date'] = officer_rows[0]['appointed_date']
            continue
        except Exception:
            pass
        
    for row in trr_df.index:
        match_options = trr_df.loc[row][match_on]
        for row2 in officer_df.index:
            comp_vals = officer_df.loc[row2][match_on]
            match_total = sum([match_options[i] == comp_vals[i] for i in match_on])
            if match_total == 2:
                trr_df.loc[row,id] = officer_df.loc[row2,id]
                # print(trr_df.loc[row,id])
                break
            elif match_total == 1:
                trr_df.loc[row,id] = officer_df.loc[row2,id]
                # print(trr_df.loc[row,id])
            # elif match_total == 2:
            #     trr_df.loc[row,id] = officer_df.loc[row2,id]
            #     # print(trr_df.loc[row,id])
            # elif match_total == 1:
            #     trr_df.loc[row,id] = officer_df.loc[row2,id]
            #     # print(trr_df.loc[row,id])
        count = count + 1
        print(count)
        print(trr_df.shape)

        if count % 100 == 0:
            trr_df.to_csv('csv/after_integration/merged.csv')
            new_df = trr_df.copy()
            dropped_tables = ['gender', 'race', 'appointed_date', 'rank', 'active', \
               'birth_year', 'first_name', 'last_name', 'tags', 'middle_initial', \
               'suffix_name', 'resignation_date', 'complaint_percentile', \
               'middle_initial2', 'civilian_allegation_percentile', \
               'honorable_mention_percentile', 'internal_allegation_percentile', \
               'trr_percentile', 'allegation_count', 'sustained_count', \
               'civilian_compliment_count', 'current_badge', 'current_salary', \
               'discipline_count', 'honorable_mention_count', 'last_unit_id', \
               'major_award_count', 'trr_count', 'unsustained_count', \
               'has_unique_name', 'created_at', 'updated_at']

            new_df=new_df.drop(dropped_tables, axis = 1)
            new_df.to_csv('csv/output/out.csv')



'''
    for row in trr_status_df.index:
        match_options = trr_status_df.loc[row][match_on]
        for row2 in officer_df.index:
            comp_vals = officer_df.loc[row2][match_on]
            match_total = sum([match_options[i] == comp_vals[i] for i in match_on])
            if match_total == 3:
                trr_status_df.loc[row,id] = officer_df.loc[row2,id]
                # print(trr_df.loc[row,id])
                break
            elif match_total == 2:
                trr_status_df.loc[row, id] = officer_df.loc[row2, id]
                # print(trr_df.loc[row,id])
            elif match_total == 1:
                trr_status_df.loc[row, id] = officer_df.loc[row2, id]
                # print(trr_df.loc[row,id])
'''






if __name__ == '__main__':
    #Type correct after OpenRefine
    file1 = 'csv/after_openrefine/postgres_public_trr_trr_refresh.csv'
    file2 = 'csv/original/postgres_public_trr_weapondischarge_refresh.csv'
    file3 = 'csv/after_openrefine/postgres_public_trr_trrstatus_refresh.csv'
    type_correct_list = [file1,file2,file3]
    # typecorrection(type_correct_list)

    #Reconciliation
    file1 = 'csv/after_typecorrection/postgres_public_trr_trr_refresh.csv'
    file2 = 'csv/after_typecorrection/postgres_public_trr_trrstatus_refresh.csv'
    recon_list = [file1,file2]
    # reconciliation(recon_list)

    #Redact correction
    file1 = 'csv/after_recon/postgres_public_trr_trr_refresh.csv'
    file2 = 'csv/after_typecorrection/postgres_public_trr_weapondischarge_refresh.csv'
    file3 = 'csv/after_recon/postgres_public_trr_trrstatus_refresh.csv'
    redact_list = [file1,file2,file3]
    # redact(redact_list)

    #Integration
    file1 = 'csv/after_redact/postgres_public_trr_trr_refresh.csv'
    file2 = 'csv/original/postgres_public_data_officer.csv'
    file3 = 'csv/after_redact/postgres_public_trr_trrstatus_refresh.csv'
    integration_list = [file1,file2,file3]
    integration(integration_list)

    file = 'postgres_public_trr_subjectweapon_refresh.csv'
    subjectweapon_df = pd.read_csv(file)
    subjectweapon_df.to_csv('csv/output/postgres_public_trr_subjectweapon_refresh.csv')





