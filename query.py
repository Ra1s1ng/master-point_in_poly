query = """
SELECT DISTINCT(device_id), utc_timestamp, horizontal_accuracy, s2_cell_id, h3_index, geo_location, partcountry, partyear, partmonth, partday
FROM "sip_refinement_db_prod"."sip_refinement_prod"
WHERE partcountry = 'DE'
  AND partyear = '2023'
  AND partmonth = '11'
  AND partday = '20'
  AND geo_location.latitude >= 52.4 AND geo_location.latitude <= 52.6
  AND geo_location.longitude >= 13.3 AND geo_location.longitude <= 13.6
LIMIT 1000000;
"""