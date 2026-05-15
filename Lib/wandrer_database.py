import database as db
import pandas as pd

def get_wandrer_totals_for_towns_for_state(states):
    in_statement = db.parameterize_SQL_in_statement(states)
    query = f'''
    select distinct town.Region, town.Country, town.State, REPLACE(town.County, ' County', '') as County
        , CASE WHEN town.Town = "Unincorporated" THEN town.Town || " " || town.County ELSE town.Town END as Town
		, town.County as LongCounty, town.long_name, town.long_county, town.detail_parent_arena_id as CountyParentArenaId
		, round(town.length, 7) as TotalMiles
		, round(town.percentage, 7) as ActualPct, round(town.ActualLength, 7) as ActualMiles
		, round(town.Pct10, 7) as Pct10, round(town.Pct25, 7) as Pct25, round(town.Pct50, 7) as Pct50
        , round(town.Pct75, 7) as Pct75, round(town.Pct90, 7) as Pct90, town.awarded
 		, CASE 
			WHEN town.percentage <= 0 then '0%' 
	-- 		WHEN town.percentage > 0 and town.percentage <= .10 then '0%' 
			WHEN town.percentage > 0 and town.ActualLength < 1 then '< 1 mile'
			WHEN town.percentage < .05 and town.ActualLength > 1 then '< 5%'
			WHEN town.percentage <= .10 and town.ActualLength >= 1 then '5%' 
			WHEN town.percentage > .10 and town.percentage < .25 then '10%'
			WHEN town.percentage >= .25 and town.percentage < .50 then '25%'
			WHEN town.percentage >= .50 and town.percentage < .75 then '50%'
			WHEN town.percentage >= .75 and town.percentage < .90 then '75%'
			WHEN town.percentage >= .90 and town.percentage < .99 then '90%'
			WHEN town.percentage >= .99 then '99%'
--			ELSE '0%'
		END as 'Award Level'
        , CASE WHEN town.Pct10Deficit < 0 THEN 0 ELSE round(town.Pct10Deficit, 7) END as Pct10Deficit
        , CASE WHEN town.Pct25Deficit < 0 THEN 0 ELSE round(town.Pct25Deficit, 7) END as Pct25Deficit
        , round(town.Pct50Deficit, 7) as Pct50Deficit, round(town.Pct75Deficit, 7) as Pct75Deficit
        , round(town.Pct90Deficit, 7) as Pct90Deficit
		, abh.geometries_visible, abh.diagonal, town.user_id, abh.seacoast, abh.osm_id, abh.update_datetime
        from vw_current_town_data_v2 town
		inner join arena_badge_header abh on abh.id = town.arena_id 
        where town.state in {in_statement}
        order by 'Award Level', town.region, town.country, town.state, town.county, town.Town
    '''
    # print(query)
    wandrerer_df = db.execute_query(query)
    wandrerer_df['Pct99Deficit'] = wandrerer_df.TotalMiles * .99 - wandrerer_df.ActualMiles
    wandrerer_df['Pct100Deficit'] = wandrerer_df.TotalMiles - wandrerer_df.ActualMiles
    wandrerer_df['Pct5Deficit'] = wandrerer_df.TotalMiles * .05 - wandrerer_df.ActualMiles
    return wandrerer_df


def get_wandrer_totals_for_counties_for_states(states):
    states_in_str = states.__str__().replace('[', '(').replace(']', ')')
    query = f'''select Region, Country, State, long_county as LongCounty
		, County
		, StateArenaId, CountyArenaId, arena_short_name
        , TotalTowns, CycledTowns, PctTownsCycled, TotalTownMiles, ActualPct, ActualMiles, AchievedTowns
        , PctTownsAchieved
 		, Pct0_Count as '0%', LT_1_Mile_Count as '< 1 mile', LT_5Pct_Count as '< 5%', Pct5_Count as '5%', Pct10_Count as '10%'
 		, Pct25_Count as '25%', Pct50_Count as '50%', Pct75_Count as '75%', Pct90_Count as '90%', Pct99_Count as '99%'
        , Pct10, Pct25, Pct50, Pct75
        , CASE WHEN Pct10Deficit < 0 THEN 0 ELSE Pct10Deficit END as Pct10Deficit
        , CASE WHEN Pct25Deficit < 0 THEN 0 ELSE Pct25Deficit END as Pct25Deficit
        , Pct50Deficit, Pct75Deficit, Pct90Deficit
        , UnincorporatedMiles, PctUnincorporatedMilesCycled, UnincorporatedMilesCycled
        , TotalCountyMiles
-- 		, TotalCountyMilesCycled, PctCountyMilesCycled
		from vw_county_aggregates 
    	where State in {states_in_str}
    	order by region, country, State, County'''
    # print(query)
    wandrerer_df = db.execute_query(query)
    return wandrerer_df


def get_wandrer_totals_for_state(state):
    query = f'''select Region, Country, State, sum(TotalTowns) as TotalTowns
		, sum(CycledTowns) as 'TownsCycled', sum(cast(CycledTowns as real))/sum(cast(TotalTowns as real)) as 'PctTownsCycled'
		, sum(AchievedTowns) as 'TownsAwarded', sum(cast(AchievedTowns as real))/sum(cast(TotalTowns as real)) as 'PctTownsAwarded'
		, sum(TotalTownMiles) as StateMiles
        , sum(TotalCountyMilesCycled) as 'TownMilesCycled', sum(TotalCountyMilesCycled)/sum(TotalTownMiles) as 'PctMilesCycled'
        , CASE WHEN sum(Pct10Deficit) < 0 THEN 0 ELSE sum(Pct10Deficit) END as 'Pct10Deficit'
        , CASE WHEN sum(Pct25Deficit) < 0 THEN 0 ELSE sum(Pct25Deficit) END as 'Pct25Deficit'
		, sum(UnincorporatedMiles) as UnincorporatedMiles
		, sum(UnincorporatedMilesCycled) as UnincorporatedMilesCycled
		, sum(UnincorporatedMilesCycled) / sum(UnincorporatedMiles) as PctUnincorporatedMilesCycled
 		, sum(Pct0_Count) as 'Pct0_Count', sum(LT_1_Mile_Count) + sum(LT_5Pct_Count) as '< Pct5_Count'
 		, sum(Pct5_Count) as 'Pct5_Count', sum(Pct10_Count) as 'Pct10_Count', sum(Pct25_Count) as 'Pct25_Count'
 		, sum(Pct50_Count) as 'Pct50_Count', sum(Pct75_Count) as 'Pct75_Count', sum(Pct90_Count) as 'Pct90_Count'
 		, sum(Pct99_Count) as 'Pct99_Count'
    	from vw_county_aggregates
    	where State = "{state}"'''
    # print(query)
    wandrerer_df = db.execute_query(query)

    # state_short_name = state.replace(' ','-').lower()
    # query2 = f'''select State.arena_name as 'State'
    #     , state.arena_mileage as TotalStateMiles
	# 	, sum(county.total) as TotalTowns, sum(county.unincorporated_miles) as UnincorporatedMiles
    #     from arena as County
    #     inner join arena State on State.arena_id = County.parent_arena_id
    #     where County.arena_short_name like '%-{state_short_name}'
    #     and County.arena_id not in (
    #         select StateArenaId from vw_county_aggregates where State = '{state}'
    #     )'''
    #
    # wandrerer2_df = execute_query(query2)
    # print(wandrerer2_df)
    return wandrerer_df

    # if wandrerer2_df['TotalTowns'].isnull().all():
    #     return wandrerer_df

    # if wandrerer2_df['TotalTowns'].isnull().all() or\
    #         math.ceil(wandrerer_df['TotalTowns'] / 10) * 10 == math.ceil(wandrerer2_df['TotalTowns'] / 10) * 10:
    #     wandrerer_df.rename(columns={'TotalTownMiles': 'TotalStateMiles'}, inplace=True)
    #     return wandrerer_df

    # # only perform this block if either all columns have values or TotalTowns value from both df are different.
    # df = pd.merge(wandrerer_df, wandrerer2_df, how='inner', on=['State'], suffixes=['1', '2'])
    # df['TotalTowns'] = df['TotalTowns1'] + df['TotalTowns2']
    # df['TotalStateMiles'] = df['TotalTownMiles'] + df['TotalCountyMiles']
    # df['UnincorporatedMiles'] = df['UnincorporatedMiles1'] + df['UnincorporatedMiles2']
    # df.drop(columns=['TotalTowns1', 'TotalTowns2', 'UnincorporatedMiles1', 'UnincorporatedMiles2', 'TotalTownMiles'
    #     , 'TotalCountyMiles'], inplace=True)
    # return df


def get_wandrer_totals_for_states(states):
    dfs = pd.DataFrame()

    for state in states:
        if dfs.empty:
            dfs = get_wandrer_totals_for_state(state)
        else:
            dfs = pd.concat([dfs, get_wandrer_totals_for_state(state)])

    return dfs


