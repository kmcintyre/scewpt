package com.socialcss.athleets.preference;

import android.os.Bundle;
import android.preference.PreferenceActivity;
import android.preference.PreferenceFragment;
import android.preference.PreferenceManager;
import android.util.Log;
import android.widget.Button;

import com.socialcss.athleets.MainActivity;
import com.socialcss.athleets.R;

import java.util.List;

public class PreferenceWithHeaders extends PreferenceActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (hasHeaders()) {
            Button button = new Button(this);
            button.setText("Some action");
            setListFooter(button);
        }
    }

    @Override
    public void onBuildHeaders(List<Header> target) {
        loadHeadersFromResource(R.xml.preference_headers, target);
    }

    @Override
    protected boolean isValidFragment(String fragmentName) {
        Log.i(MainActivity.TAG, "isValidFragment:" + fragmentName);
        return true;
    }

    public static class Prefs1Fragment extends PreferenceFragment {
        @Override
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            PreferenceManager.setDefaultValues(getActivity(),
                    R.xml.advanced_preferences, false);
            addPreferencesFromResource(R.xml.fragmented_preferences);
        }
    }

    public static class Prefs1FragmentInner extends PreferenceFragment {
        @Override
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            addPreferencesFromResource(R.xml.fragmented_preferences_inner);
        }
    }

    public static class Prefs2Fragment extends PreferenceFragment {
        @Override
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            addPreferencesFromResource(R.xml.preference_dependencies);
        }
    }
}