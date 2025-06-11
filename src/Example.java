package com.example;

import java.util.List;
import java.util.ArrayList;

/**
 * Example Java class to demonstrate Checkstyle linting.
 */
public class Example {
    private static final String CONSTANT = "value";
    private String field;
    
    public Example() {
        this.field = "default";
    }
    
    public void method() {
        List<String> list = new ArrayList<>();
        list.add("item");
        
        for (String item : list) {
            System.out.println(item);
        }
    }
    
    public String getField() {
        return field;
    }
    
    public void setField(String field) {
        this.field = field;
    }
} 