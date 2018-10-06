package com.socialcss.athleets;

import android.graphics.Bitmap;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.CardView;
import android.os.Bundle;
import android.util.Log;
import android.util.TypedValue;
import android.widget.LinearLayout;
import android.widget.LinearLayout.LayoutParams;
import android.widget.TextView;

import com.android.volley.Response;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.NetworkImageView;
import com.google.gson.Gson;
import com.socialcss.athleets.com.socialcss.model.Entity;
import com.socialcss.athleets.com.socialcss.model.Operator;
import com.socialcss.athleets.util.SortByTwitterCount;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Arrays;
import java.util.Collections;

public class LeaguesActivity extends AppCompatActivity {

    private LinearLayout layout;
    private static final Gson gson = new Gson();

    LayoutParams params = new LayoutParams(
        LayoutParams.WRAP_CONTENT,
        LayoutParams.WRAP_CONTENT
    );

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_leagues);
        layout = this.findViewById(R.id.leagues);
        getLeagues();
    }

    private void getLeagues() {
        Log.i(MainActivity.TAG, "getLeagues");
        String operator_url = new String("http://service.athleets.com/site/operator");
        Response.Listener<JSONArray> operator_listener = new Response.Listener<JSONArray>() {
            @Override
            public void onResponse(JSONArray operator_response) {
                Operator[] operators = gson.fromJson(operator_response.toString(), Operator[].class);
                Arrays.sort(operators, new SortByTwitterCount());
                Collections.reverse(Arrays.asList(operators));
                for (final Operator operator: operators) {
                    Log.i(MainActivity.TAG, "Operator: " + operator.getRole());

                    String league_url = new String("http://service.athleets.com/site/league/" + operator.getRole());

                    Response.Listener<JSONObject> league_listener = new Response.Listener<JSONObject>() {

                        @Override
                        public void onResponse(JSONObject league_response) {
                            Entity league = gson.fromJson(league_response.toString(), Entity.class);
                            CardView card = new CardView(getApplicationContext());
                            //card.setRadius(20);
                            card.setContentPadding(2, 0, 2, 2);
                            card.setCardBackgroundColor(Color.parseColor("#FFC6D6C3"));
                            card.setMaxCardElevation(20);
                            card.setCardElevation(20);
                            card.setUseCompatPadding(true);

                            String background_url = "http://athleets.com/tw/" + league.getTwitter_id() + "/background.png";
                            Log.i(MainActivity.TAG, "League:" + league.getLeague() + " Background: " + background_url);

                            NetworkImageView background_view = new NetworkImageView(getApplicationContext());
                            background_view.setLayoutParams(params);
                            background_view.setImageUrl(background_url, NetworkRequests.getInstance(getApplicationContext()).getImageLoader());

                            card.addView(background_view);

                            TextView tv = new TextView(getApplicationContext());
                            tv.setLayoutParams(params);
                            tv.setText(league.getLeague() + " " + Integer.toString(operator.getTwitter_count()));
                            tv.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 30);
                            tv.setTextColor(Color.RED);

                            card.addView(tv);
                            layout.addView(card);
                        }
                    };

                    JsonObjectRequest league_request = new JsonObjectRequest(league_url, null, league_listener, NetworkRequests.getInstance(getApplicationContext()).getErrorListener());
                    NetworkRequests.getInstance(getApplicationContext()).getRequestQueue().add(league_request);
                }
            }
        };
        JsonArrayRequest operator_request = new JsonArrayRequest(operator_url, operator_listener, NetworkRequests.getInstance(getApplicationContext()).getErrorListener());
        NetworkRequests.getInstance(getApplicationContext()).getRequestQueue().add(operator_request);
    }

}
