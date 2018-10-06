package com.socialcss.athleets;

import android.content.Intent;
import android.support.constraint.ConstraintLayout;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.ContentFrameLayout;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import com.socialcss.athleets.preference.PreferenceWithHeaders;
import com.twitter.sdk.android.core.Result;
import com.twitter.sdk.android.core.Twitter;

import java.net.URI;
import java.net.URISyntaxException;

import tech.gusavila92.websocketclient.WebSocketClient;

import com.twitter.sdk.android.core.Callback;
import com.twitter.sdk.android.core.models.Tweet;
import com.twitter.sdk.android.core.TwitterException;
import com.twitter.sdk.android.tweetui.TweetUtils;
import com.twitter.sdk.android.tweetui.TweetView;

import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private Toolbar toolbar;
    private WebSocketClient webSocketClient;
    public static final String TAG = "athleets.com.echo";


    private void embedTweet(long tweetId) {

        final ContentFrameLayout myLayout = (ContentFrameLayout)findViewById(android.R.id.content);

        TweetUtils.loadTweet(tweetId, new Callback<Tweet>() {
            @Override
            public void success(Result<Tweet> result) {
                myLayout.addView(new TweetView(MainActivity.this, result.data));
            }

            @Override
            public void failure(TwitterException exception) {
                Toast.makeText(MainActivity.this, exception.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }


    private void createWebSocketClient() {
        URI uri;
        try {
            uri = new URI("ws://service.athleets.com:8080/");
        }
        catch (URISyntaxException e) {
            e.printStackTrace();
            return;
        }

        webSocketClient = new WebSocketClient(uri) {
            @Override
            public void onOpen() {
                Log.i(TAG, "onOpen");
                //webSocketClient.send("Hello, World!");
            }

            @Override
            public void onTextReceived(String message) {
                Log.i(TAG, "onTextReceived:" + message);
                try {
                    JSONObject obj = new JSONObject(message);
                    embedTweet(Long.valueOf(obj.get("_tweet_id").toString()));
                } catch (Exception e) {
                    Log.e(TAG, e.getMessage());
                }

            }

            @Override
            public void onBinaryReceived(byte[] data) {
                Log.i(TAG, "onBinaryReceived");
            }

            @Override
            public void onPingReceived(byte[] data) {
                Log.i(TAG, "onPingReceived");
            }

            @Override
            public void onPongReceived(byte[] data) {
                Log.i(TAG, "onPongReceived");
            }

            @Override
            public void onException(Exception e) {
                Log.i(TAG, e.getMessage());
            }

            @Override
            public void onCloseReceived() {
                Log.i(TAG, "onCloseReceived");
            }
        };

        webSocketClient.setConnectTimeout(10000);
        webSocketClient.setReadTimeout(60000);
        webSocketClient.addHeader("Origin", "http://athleets.com");
        webSocketClient.enableAutomaticReconnection(5000);
        webSocketClient.connect();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTheme(R.style.AppTheme);
        setContentView(R.layout.activity_main);
        toolbar = (Toolbar)findViewById(R.id.app_bar);
        toolbar.setTitle(R.string.app_name);
        toolbar.setSubtitle(R.string.app_subtitle);
        setSupportActionBar(toolbar);
        //Twitter.initialize(this);
        //createWebSocketClient();
    }

    /** Called when the user touches the button */
    public void sendMessage(View view) {
        Log.e(TAG, "sendMessage");
        Intent intent = new Intent(this, PreferenceWithHeaders.class);
        startActivity(intent);
    }
}
