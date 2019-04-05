/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package gov.nasa.worldwindx.examples;

import java.util.ArrayList;

/**
 *
 * @author kevyn
 */
public class AircraftT {
    
    public double time;
    public ArrayList<Aircraft> aircraftsT = new ArrayList<Aircraft>();
    
    public AircraftT(double time){
        this.time = time;
    }
    
}
