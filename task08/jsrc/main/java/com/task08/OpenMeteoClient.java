// layer/java/lib/com/task08/OpenMeteoClient.java

package com.task08;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class OpenMeteoClient {
    private static final String BASE_URL = "https://api.open-meteo.com/v1/forecast";

    public String getWeatherForecast(double latitude, double longitude) throws Exception {
        String url = String.format("%s?latitude=%.4f&longitude=%.4f&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m",
                BASE_URL, latitude, longitude);

        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("GET");

        int responseCode = con.getResponseCode();
        if (responseCode == HttpURLConnection.HTTP_OK) { // success
            BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            return response.toString();
        } else {
            throw new Exception("GET request failed with response code: " + responseCode);
        }
    }
}
