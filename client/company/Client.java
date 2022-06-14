package org.example;

import java.io.*;

import okhttp3.*;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import org.jetbrains.annotations.NotNull;
import org.json.JSONException;
import org.json.JSONObject;

public class Client {
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    private static final MediaType IMAGE = MediaType.get("image/png");

    public static void httpClientRequest(List<File> files, File result) throws AppException, IOException {
        String token = UUID.randomUUID().toString();
        String url = "https://c7df-78-140-249-142.eu.ngrok.io/";
//        String url = "http://127.0.0.1:8000/";
        System.out.println(token);
        OkHttpClient client = new OkHttpClient.Builder().readTimeout(300, TimeUnit.MINUTES)
                .addInterceptor(new Interceptor() {
                    @NotNull
                    @Override
                    public Response intercept(@NotNull Chain chain) throws IOException {
                        String credential = Credentials.basic("username", "password");
                        Request request = chain.request();
                        Request authenticatedRequest = request.newBuilder()
                                .header("Authorization", credential).build();
                        return chain.proceed(authenticatedRequest);
                    }
                })
                .build();
        initializationHTTPPOSTRequest(client, url, token, files.size());
        for (File file : files) {
            sendFileHTTPPOSTRequest(client, url, token, file);
        }

        getFileHTTPGETRequest(client, url, token, result);
    }

    private static void initializationHTTPPOSTRequest(OkHttpClient client, String url, String token, long numberOfFiles) throws AppException {
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("id", token);
            jsonObject.put("count", numberOfFiles);
        } catch (JSONException e) {
            throw new AppException("Can't make json to initialize reconstruction", e);
        }

        RequestBody body = RequestBody.create(jsonObject.toString(), JSON);
        Request requestIni = new Request.Builder()
                .url(HttpUrl.get(url + token + ".json"))
                .post(body)
                .header("Content-Type", "application/json")
                .build();

        try (Response response = client.newCall(requestIni).execute()) {
            if (response.isSuccessful()) {
                System.out.println("Send initialization: Ok");
            }
        } catch (IOException e) {
            throw new AppException("Can't make initialization request", e);
        }

    }

    private static void sendFileHTTPPOSTRequest(OkHttpClient client, String url, String token, File file) throws AppException, IOException {
        RequestBody body = RequestBody.create(file, IMAGE);
        Request requestIni = new Request.Builder()
                .url(HttpUrl.get(url + token + "/images/" + file.getName()))
                .post(body)
                .header("Content-Type", "image/png")
                .build();
        try (Response response = client.newCall(requestIni).execute()) {
            if (response.isSuccessful()) {
                System.out.println("Send file " + file.getName() + " : Ok");
            }
        } catch (IOException e) {
            throw new AppException("Can't send file " + file.getName(), e);
        }
    }

    private static void getFileHTTPGETRequest(OkHttpClient client, String url, String token, File result) throws AppException {
        Request requestGet = new Request.Builder()
                .url(HttpUrl.get(url + "resources/" + token + "/res.png"))
//                .url(HttpUrl.get(url + "resources/" + token + "/reconstruction_sequential/PMVS/models/pmvs_options.txt.ply"))
                .get()
                .build();
        try (Response response = client.newCall(requestGet).execute()) {
            if (response.isSuccessful()) {
                try (FileOutputStream stream = new FileOutputStream(result)) {
                    ResponseBody body = response.body();
                    if (body != null) {
                        stream.write(body.bytes());
                    }
                }
            } else {
                System.out.println("wtf");
            }
        } catch (IOException e) {
            throw new AppException("Can't get result", e);
        }
    }

    public static void main(String[] args) throws InterruptedException {
        File res = new File("test/res.png");
        List<File> files = new ArrayList<>();
        files.add(new File("test/im1.png"));
        files.add(new File("test/im2.png"));
        ArrayList<Thread> lst = new ArrayList<>();
        long start = System.currentTimeMillis();
        for (int i = 0; i < 1; i++) {
            Thread.sleep(1000);
            Thread thr = new Thread(() -> {
                try {
                    httpClientRequest(files, res);
                } catch (AppException | IOException e) {
                    e.printStackTrace();
                }
            });
            lst.add(thr);
            thr.start();
        }
        for (int i = 0; i < 1; i++) {
            lst.get(i).join();
        }
        long end = System.currentTimeMillis();
        System.out.println((end - start));
    }
}
