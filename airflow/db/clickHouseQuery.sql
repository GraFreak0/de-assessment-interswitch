WITH trip_metrics AS (
    SELECT 
        DATE_FORMAT(pickup_datetime, '%Y-%m') AS month,
        DAYOFWEEK(pickup_datetime) AS day_of_week,
        COUNT(*) AS total_trips,
        AVG(fare_amount) AS avg_fare_per_trip,
        AVG(TIMESTAMPDIFF(MINUTE, pickup_datetime, dropoff_datetime)) AS avg_duration_per_trip
    FROM tripdata
    WHERE pickup_datetime BETWEEN '2014-01-01' AND '2016-12-31'
    GROUP BY month, day_of_week
)
SELECT 
    month,
    AVG(CASE WHEN day_of_week = 7 THEN total_trips END) AS sat_mean_trip_count,
    AVG(CASE WHEN day_of_week = 7 THEN avg_fare_per_trip END) AS sat_mean_fare_per_trip,
    AVG(CASE WHEN day_of_week = 7 THEN avg_duration_per_trip END) AS sat_mean_duration_per_trip,
    AVG(CASE WHEN day_of_week = 1 THEN total_trips END) AS sun_mean_trip_count,
    AVG(CASE WHEN day_of_week = 1 THEN avg_fare_per_trip END) AS sun_mean_fare_per_trip,
    AVG(CASE WHEN day_of_week = 1 THEN avg_duration_per_trip END) AS sun_mean_duration_per_trip
FROM trip_metrics
GROUP BY month
ORDER BY month;
