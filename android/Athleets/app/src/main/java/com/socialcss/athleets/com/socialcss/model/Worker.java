package com.socialcss.athleets.com.socialcss.model;

import java.util.List;

import lombok.Data;

/**
 * Created by ubuntu on 2/8/18.
 */

@Data
public class Worker {

    private String role;
    private String twitter;

    private Integer twitter_count;
    private Integer instagram_count;
    private Integer entity_count;
    private Integer team_count;
    private Integer facebook_count;

    private List<String> site_leagues;
}
