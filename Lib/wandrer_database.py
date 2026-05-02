import database as db

def get_wandrer_totals_for_towns_for_state(states):
    in_statement = db.parameterize_SQL_in_statement(states)
    query = f'''select distinct fqtn.Region, fqtn.Country, fqtn.State, REPLACE(fqtn.County, ' County', '') as County
        , CASE WHEN fqtn.name = "Unincorporated" THEN fqtn.name || " " || fqtn.County ELSE fqtn.name END as Town
		, fqtn.County as LongCounty, fqtn.long_name, fqtn.CountyLongName, town.parent_arena_id as CountyParentArenaId
		, round(fqtn.length, 7) as TotalMiles
		, round(fqtn.percentage, 7) as ActualPct, round(fqtn.ActualLength, 7) as ActualMiles
		, round(fqtn.Pct10, 7) as Pct10, round(fqtn.Pct25, 7) as Pct25, round(fqtn.Pct50, 7) as Pct50
        , round(fqtn.Pct75, 7) as Pct75, round(fqtn.Pct90, 7) as Pct90, fqtn.awarded
 		, CASE 
			WHEN fqtn.percentage <= 0 then '0%' 
	-- 		WHEN fqtn.percentage > 0 and fqtn.percentage <= .10 then '0%' 
			WHEN fqtn.percentage > 0 and fqtn.ActualLength < 1 then '< 1 mile'
			WHEN fqtn.percentage < .05 and fqtn.ActualLength > 1 then '< 5%'
			WHEN fqtn.percentage <= .10 and fqtn.ActualLength >= 1 then '5%' 
			WHEN fqtn.percentage > .10 and fqtn.percentage < .25 then '10%'
			WHEN fqtn.percentage >= .25 and fqtn.percentage < .50 then '25%'
			WHEN fqtn.percentage >= .50 and fqtn.percentage < .75 then '50%'
			WHEN fqtn.percentage >= .75 and fqtn.percentage < .90 then '75%'
			WHEN fqtn.percentage >= .90 and fqtn.percentage < .99 then '90%'
			WHEN fqtn.percentage >= .99 then '99%'
--			ELSE '0%'
		END as 'Award Level'
        , CASE WHEN fqtn.Pct10Deficit < 0 THEN 0 ELSE round(fqtn.Pct10Deficit, 7) END as Pct10Deficit
        , CASE WHEN fqtn.Pct25Deficit < 0 THEN 0 ELSE round(fqtn.Pct25Deficit, 7) END as Pct25Deficit
        , round(fqtn.Pct50Deficit, 7) as Pct50Deficit, round(fqtn.Pct75Deficit, 7) as Pct75Deficit
        , round(fqtn.Pct90Deficit, 7) as Pct90Deficit
		, fqtn.geometries_visible, fqtn.diagonal, fqtn.user_id, town.seacoast, town.osm_id, town.update_datetime
        from vw_current_town_data town
		inner join vw_current_town_data fqtn on fqtn.id = town.id 
        where fqtn.state in {in_statement}
        order by 'Award Level', fqtn.region, fqtn.country, fqtn.state, fqtn.county, fqtn.name'''
    # print(query)
    wandrerer_df = db.execute_query(query)
    wandrerer_df['Pct99Deficit'] = wandrerer_df.TotalMiles * .99 - wandrerer_df.ActualMiles
    wandrerer_df['Pct100Deficit'] = wandrerer_df.TotalMiles - wandrerer_df.ActualMiles
    wandrerer_df['Pct5Deficit'] = wandrerer_df.TotalMiles * .05 - wandrerer_df.ActualMiles
    return wandrerer_df
