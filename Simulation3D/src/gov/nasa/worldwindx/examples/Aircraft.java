/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package gov.nasa.worldwindx.examples;

/**
 *
 * @author kevyn
 */
public class Aircraft {
    
    public String callSign;
    public double time;
    public double latitude;
    public double longitude;
    public double altitude;
    public double heading;
    public boolean onRa;
    public boolean onCrash;
    public boolean isReal;
    
    public Aircraft(String callSign, double time, double latitude, double longitude, double altitude, double heading, boolean onRa, boolean onCrash, boolean isReal){
        this.callSign = callSign;
        this.time = time;
        this.latitude = latitude;
        this.longitude = longitude;
        this.altitude = altitude;
        this.heading = heading;
        this.onRa = onRa;
        this.onCrash = onCrash;
        this.isReal = isReal;
    }
    
}
