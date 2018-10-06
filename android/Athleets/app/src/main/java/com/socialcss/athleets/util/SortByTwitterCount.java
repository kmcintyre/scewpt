package com.socialcss.athleets.util;

import com.socialcss.athleets.com.socialcss.model.Worker;

import java.util.Comparator;

/**
 * Created by kmcintyre1 on 2/14/18.
 */

public class SortByTwitterCount implements Comparator<Worker> {

    public int compare(Worker a, Worker b) {
        if ( a.getTwitter_count() == b.getTwitter_count() ) {
            return 0;
        } else if ( a.getTwitter_count() > b.getTwitter_count() ) {
            return 1;
        }
        return -1;
    }
}
