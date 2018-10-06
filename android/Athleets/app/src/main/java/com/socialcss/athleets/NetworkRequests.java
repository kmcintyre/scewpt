package com.socialcss.athleets;

import android.content.Context;
import android.graphics.Bitmap;
import android.util.Log;
import android.util.LruCache;

import com.android.volley.Cache;
import com.android.volley.Network;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.BasicNetwork;
import com.android.volley.toolbox.DiskBasedCache;
import com.android.volley.toolbox.HurlStack;
import com.android.volley.toolbox.ImageLoader;

import lombok.Getter;

/**
 * Created by ubuntu on 2/8/18.
 */

public class NetworkRequests {

    private static NetworkRequests instance = null;

    @Getter
    private RequestQueue requestQueue;
    @Getter
    private ImageLoader imageLoader;
    @Getter
    Response.ErrorListener errorListener = new Response.ErrorListener() {
        @Override
        public void onErrorResponse(VolleyError error) {
        Log.e(MainActivity.TAG, "Response: " + error.toString());
        }
    };

    private Cache diskCache;
    private Network network = new BasicNetwork(new HurlStack());

    protected NetworkRequests(Context context) {
        Log.i(MainActivity.TAG, "CacheDir:" + context.getCacheDir().toString());
        this.diskCache = new DiskBasedCache(context.getCacheDir(), 1024 * 1024);
        this.requestQueue = new RequestQueue(diskCache, network);
        this.requestQueue.start();
        this.imageLoader = new ImageLoader(this.requestQueue, new ImageLoader.ImageCache() {
            private final LruCache<String, Bitmap> lruCache = new LruCache<String, Bitmap>(50);
            public void putBitmap(String url, Bitmap bitmap) {
                lruCache.put(url, bitmap);
            }
            public Bitmap getBitmap(String url) {
                return lruCache.get(url);
            }
        });
    }

    public static synchronized NetworkRequests getInstance(Context context) {
        if (instance == null) {
            instance = new NetworkRequests(context);
        }
        return instance;
    }

}
