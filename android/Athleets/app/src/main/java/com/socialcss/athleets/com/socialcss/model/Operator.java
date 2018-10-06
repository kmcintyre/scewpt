package com.socialcss.athleets.com.socialcss.model;

import java.util.Map;

import lombok.Data;

/**
 * Created by ubuntu on 2/8/18.
 */

@Data
public class Operator extends Worker {


    private String name;
    private String origin;
    private String description;

    private Map<String,String> lingo;

}
