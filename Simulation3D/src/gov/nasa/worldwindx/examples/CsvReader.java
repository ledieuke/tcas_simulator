/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package gov.nasa.worldwindx.examples;

import com.opencsv.CSVReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

/**
 *
 * @author kevyn
 */
public class CsvReader {
    
    public ArrayList<AircraftT> aircrafts = new ArrayList<AircraftT>();
    public String csv_name;
    
    public CsvReader(ArrayList<AircraftT> aircrafts){
        this.aircrafts = aircrafts;
    }
    
    public void readCsv() throws FileNotFoundException, IOException{
    String fileName = "../simulation/results/extract_results.csv";
        
    CSVReader reader = new CSVReader(new FileReader(fileName),',', '"', 1);
        
    String[] nextLine;
    double currentTime = -1;
        
    while ((nextLine = reader.readNext()) != null) {
        if (nextLine != null) {
            boolean onRa;
            boolean onCrash;
            boolean isReal;
            boolean adsbOutStatus;
            if(nextLine[9].equals("True") == true){
                onRa = true;
            } 
            else {
                onRa = false;
            }
            if(nextLine[10].equals("True") == true){
                onCrash = true;
            } 
            else {
                onCrash = false;
            }
            if(nextLine[11].equals("True") == true){
                isReal = true;
            } 
            else {
                isReal = false;
            }
            if(nextLine[12].equals("True") == true){
                adsbOutStatus = true;
            } 
            else {
                adsbOutStatus = false;
            }
            if(Math.abs(currentTime - Double.parseDouble(nextLine[0])) < 1e-10){
                this.aircrafts.get(aircrafts.size()-1).aircraftsT.add(new Aircraft(nextLine[1], Double.parseDouble(nextLine[0]), Double.parseDouble(nextLine[5]), Double.parseDouble(nextLine[6]), Double.parseDouble(nextLine[4]), Double.parseDouble(nextLine[7]), onRa, onCrash, isReal, adsbOutStatus));
            }
            else{
                this.aircrafts.add(new AircraftT(Double.parseDouble(nextLine[0])));
                this.aircrafts.get(aircrafts.size()-1).aircraftsT.add(new Aircraft(nextLine[1], Double.parseDouble(nextLine[0]), Double.parseDouble(nextLine[5]), Double.parseDouble(nextLine[6]), Double.parseDouble(nextLine[4]), Double.parseDouble(nextLine[7]), onRa, onCrash, isReal, adsbOutStatus));
            }
            currentTime = Double.parseDouble(nextLine[0]);
//            Verifying the read data here
//                System.out.println(nextLine[0]);
//                System.out.println(Arrays.toString(nextLine));
            }
        }
    }
}
