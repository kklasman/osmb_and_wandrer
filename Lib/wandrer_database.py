import database as db

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
        where town.state in ({in_statement})
        order by 'Award Level', town.region, town.country, town.state, town.county, town.Town
    '''
    # print(query)
    wandrerer_df = db.execute_query(query)
    wandrerer_df['Pct99Deficit'] = wandrerer_df.TotalMiles * .99 - wandrerer_df.ActualMiles
    wandrerer_df['Pct100Deficit'] = wandrerer_df.TotalMiles - wandrerer_df.ActualMiles
    wandrerer_df['Pct5Deficit'] = wandrerer_df.TotalMiles * .05 - wandrerer_df.ActualMiles
    return wandrerer_df
