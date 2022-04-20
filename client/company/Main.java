package com.company;

import java.io.*;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.UUID;
import org.json.JSONObject;

public class Main {

    public static void main(String[] args) throws IOException, InterruptedException {
        httpClientRequest();
    }

    private static void initializationHTTPPOSTRequest(HttpClient client, String url, String token) throws FileNotFoundException {
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("id", token);
        jsonObject.put("count", "2"); // size of dir or number of selected
        try {
            FileWriter file = new FileWriter("test/ini.json");
            file.write(jsonObject.toString());
            file.close();
        } catch (IOException e) {
            e.printStackTrace();
        }


        HttpRequest requestIni = HttpRequest.newBuilder()
                .uri(URI.create(url + token + ".json"))
                .POST(HttpRequest.BodyPublishers.ofFile(Paths.get("test/ini.json")))
                .version(HttpClient.Version.HTTP_1_1)
                .header("Content-Type", "application/json")
                .build();
        try {
            HttpResponse<String> response = client.send(requestIni, HttpResponse.BodyHandlers.ofString());
            System.out.println(response.statusCode());
        } catch (IOException | InterruptedException e) {
            //e.printStackTrace();
        }
    }

    private static void sendFileHTTPPOSTRequest(HttpClient client, String url, String token, String filePath) throws FileNotFoundException {
        HttpRequest requestIni = HttpRequest.newBuilder()
                .uri(URI.create(url + token + '/' + Paths.get(filePath).getFileName().toString()))
                .POST(HttpRequest.BodyPublishers.ofFile(Paths.get(filePath)))
                .version(HttpClient.Version.HTTP_1_1)
                .header("Content-Type", "image/png")
                .build();
        try {
            HttpResponse<String> response = client.send(requestIni, HttpResponse.BodyHandlers.ofString());
            System.out.println(response.statusCode());
        } catch (IOException | InterruptedException e) {
            //e.printStackTrace();
        }
    }

    private static void getFileHTTPGETRequest(HttpClient client, String url, String token, String resultPath) throws IOException, InterruptedException {
        HttpRequest requestGet = HttpRequest.newBuilder()
                .uri(URI.create(url + "resources/" + token + "/res.png"))
                .GET()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        HttpResponse<byte[]> response = client.send(requestGet, HttpResponse.BodyHandlers.ofByteArray());

        Files.write(Path.of(resultPath), response.body(), StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
        System.out.println(response.statusCode());
    }

    private static void httpClientRequest() throws IOException, InterruptedException {
        String token = UUID.randomUUID().toString();
        String url = "http://localhost:8000/";
        System.out.println(token);
        HttpClient client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        initializationHTTPPOSTRequest(client, url, token);

        sendFileHTTPPOSTRequest(client, url, token, "test/im1.png"); // в цикле отправить все фотки
        sendFileHTTPPOSTRequest(client, url, token, "test/im2.png");

        getFileHTTPGETRequest(client, url, token, "test/res.png");
    }

    private static void curlRequest() throws InterruptedException, IOException { // just old example
        String command2 = "curl -X POST -H Content-Type:application/json --data-binary @./ini.json http://localhost:8000/12345.json";
        Process process2 = Runtime.getRuntime().exec(command2);
        process2.getOutputStream();
        process2.waitFor();
        System.out.println(process2.exitValue());

        String command1 = "curl -X POST -H Content-Type:image/png --data-binary @./im1.png http://localhost:8000/12345/im.png";
        Process process1 = Runtime.getRuntime().exec(command1);
        process1.getOutputStream();
        process1.waitFor();
        System.out.println(process1.exitValue());

        String command3 = "curl -X GET localhost:8000/12345/res.png --output result.png";
        Process process3 = Runtime.getRuntime().exec(command3);
        process3.getOutputStream();
        process3.waitFor();
        System.out.println(process3.exitValue());

    }
}
