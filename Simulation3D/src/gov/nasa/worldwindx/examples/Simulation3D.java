package gov.nasa.worldwindx.examples;

import gov.nasa.worldwind.WorldWind;
import gov.nasa.worldwind.WorldWindow;
import gov.nasa.worldwind.avlist.AVKey;
import gov.nasa.worldwind.event.PositionEvent;
import gov.nasa.worldwind.event.PositionListener;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.layers.RenderableLayer;
import gov.nasa.worldwind.render.BasicShapeAttributes;
import gov.nasa.worldwind.render.Ellipsoid;
import gov.nasa.worldwind.render.Material;
import gov.nasa.worldwind.render.ShapeAttributes;
import gov.nasa.worldwind.util.BasicDragger;
import static gov.nasa.worldwindx.examples.ApplicationTemplate.insertBeforeCompass;
import javax.swing.*;
import javax.swing.event.*;
import java.awt.*;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;

/**
 * This example demonstrates the use of multiple WMS layers, as displayed in a WMSLayersPanel.
 *
 * @author tag
 * @version $Id: WMSLayerManager.java 2109 2014-06-30 16:52:38Z tgaskins $
 */
public class Simulation3D extends ApplicationTemplate
{
   protected static final String[] servers = new String[]
        {
            "https://neowms.sci.gsfc.nasa.gov/wms/wms",
        };

    protected static final class AppFrame extends ApplicationTemplate.AppFrame
    {
        protected final Dimension wmsPanelSize = new Dimension(400, 600);
        protected JTabbedPane tabbedPane;
        protected int previousTabIndex;
        
        public ArrayList<AircraftT> aircrafts = new ArrayList<AircraftT>();
        
        public int t = 0;
        public ArrayList<Position> explosions = new ArrayList<Position>();
        public ArrayList<String> destroyed = new ArrayList<String>();
        public ArrayList<Integer> explosionTimes = new ArrayList<Integer>();
        public double factor = 40;
        public double height = 60*1852*0.33*factor;
        public int separation = 10;

        public void initAircrafts() throws IOException{
            CsvReader csvReader = new CsvReader(this.aircrafts);
            csvReader.readCsv();
        }
        
        public void drawSquare(RenderableLayer layer, int t, ShapeAttributes attrs, Aircraft a){
            ArrayList positions_top = new ArrayList();
            double heading = Math.toRadians(a.heading);
            positions_top.add(Position.fromDegrees(a.latitude+Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_top.add(Position.fromDegrees(a.latitude+Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_top.add(Position.fromDegrees(a.latitude-Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_top.add(Position.fromDegrees(a.latitude-Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            gov.nasa.worldwind.render.Polygon trail_top = new gov.nasa.worldwind.render.Polygon(positions_top);
            trail_top.setAltitudeMode(WorldWind.ABSOLUTE);
            trail_top.setAttributes(attrs);
            trail_top.setVisible(true);
            trail_top.setValue(AVKey.DISPLAY_NAME, a.callSign);
            layer.addRenderable(trail_top);
            ArrayList positions_below = new ArrayList();
            positions_below.add(Position.fromDegrees(a.latitude+Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_below.add(Position.fromDegrees(a.latitude+Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_below.add(Position.fromDegrees(a.latitude-Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_below.add(Position.fromDegrees(a.latitude-Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            gov.nasa.worldwind.render.Polygon trail_below = new gov.nasa.worldwind.render.Polygon(positions_below);
            trail_below.setAltitudeMode(WorldWind.ABSOLUTE);
            trail_below.setAttributes(attrs);
            trail_below.setVisible(true);
            trail_below.setValue(AVKey.DISPLAY_NAME, a.callSign);
            layer.addRenderable(trail_below);
            ArrayList positions_front = new ArrayList();
            positions_front.add(Position.fromDegrees(a.latitude+Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_front.add(Position.fromDegrees(a.latitude+Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_front.add(Position.fromDegrees(a.latitude+Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_front.add(Position.fromDegrees(a.latitude+Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            gov.nasa.worldwind.render.Polygon trail_front = new gov.nasa.worldwind.render.Polygon(positions_front);
            trail_front.setAltitudeMode(WorldWind.ABSOLUTE);
            trail_front.setAttributes(attrs);
            trail_front.setVisible(true);
            trail_front.setValue(AVKey.DISPLAY_NAME, a.callSign);
            layer.addRenderable(trail_front);
            ArrayList positions_back = new ArrayList();
            positions_back.add(Position.fromDegrees(a.latitude+Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_back.add(Position.fromDegrees(a.latitude-Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_back.add(Position.fromDegrees(a.latitude-Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_back.add(Position.fromDegrees(a.latitude+Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            gov.nasa.worldwind.render.Polygon trail_back = new gov.nasa.worldwind.render.Polygon(positions_back);
            trail_back.setAltitudeMode(WorldWind.ABSOLUTE);
            trail_back.setAttributes(attrs);
            trail_back.setVisible(true);
            trail_back.setValue(AVKey.DISPLAY_NAME, a.callSign);
            layer.addRenderable(trail_back);
            ArrayList positions_left = new ArrayList();
            positions_left.add(Position.fromDegrees(a.latitude-Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_left.add(Position.fromDegrees(a.latitude-Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_left.add(Position.fromDegrees(a.latitude-Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_left.add(Position.fromDegrees(a.latitude-Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude-(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            gov.nasa.worldwind.render.Polygon trail_left = new gov.nasa.worldwind.render.Polygon(positions_left);
            trail_left.setAltitudeMode(WorldWind.ABSOLUTE);
            trail_left.setAttributes(attrs);
            trail_left.setVisible(true);
            trail_left.setValue(AVKey.DISPLAY_NAME, a.callSign);
            layer.addRenderable(trail_left);
            ArrayList positions_right = new ArrayList();
            positions_right.add(Position.fromDegrees(a.latitude+Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_right.add(Position.fromDegrees(a.latitude-Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude+height/2));
            positions_right.add(Position.fromDegrees(a.latitude-Math.sin(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.cos(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            positions_right.add(Position.fromDegrees(a.latitude+Math.cos(heading - Math.PI/4)*factor/2.82, a.longitude+(Math.sin(heading - Math.PI/4)*factor/Math.cos(Math.toRadians(a.latitude)))/2.82, a.altitude-height/2));
            gov.nasa.worldwind.render.Polygon trail_right = new gov.nasa.worldwind.render.Polygon(positions_right);
            trail_right.setAltitudeMode(WorldWind.ABSOLUTE);
            trail_right.setAttributes(attrs);
            trail_right.setVisible(true);
            trail_right.setValue(AVKey.DISPLAY_NAME, a.callSign);
            layer.addRenderable(trail_right);
        }
        
        public void drawExplosion(RenderableLayer layer, ShapeAttributes attrs, Position position){
            attrs.setInteriorMaterial(Material.RED);
            Ellipsoid explosion = new Ellipsoid(position, 200000*factor, 200000*factor, 200000*factor);
            explosion.setAltitudeMode(WorldWind.ABSOLUTE);
            explosion.setAttributes(attrs);
            explosion.setVisible(true);
            layer.addRenderable(explosion);            
        }
        
        public void draw(RenderableLayer layer, int t){
            int i = 0;
            for (Aircraft a : aircrafts.get(t).aircraftsT) {
                ShapeAttributes attrs = new BasicShapeAttributes();
                attrs.setInteriorOpacity(1);
                attrs.setEnableLighting(true);
                attrs.setOutlineMaterial(Material.BLACK);
                attrs.setOutlineWidth(2d);
                attrs.setDrawInterior(true);
                attrs.setDrawOutline(true);
                boolean isDestroyed = false;
                if(destroyed.contains(a.callSign) && a.isReal){
                    int index = destroyed.indexOf(a.callSign);
                    int explosionTime = explosionTimes.get(index);
                    if(t >= explosionTime){
                        isDestroyed = true;
                    }
                    else{
                        explosions.remove(index);
                        explosionTimes.remove(index);
                        destroyed.remove(index);
                    }
                }
                if(a.onCrash && !destroyed.contains(a.callSign)){
                    destroyed.add(a.callSign);
                    explosionTimes.add(t);
                    explosions.add(Position.fromDegrees(a.latitude, a.longitude, a.altitude));
                }
                else if(!isDestroyed){
                    if(a.onRa){
                        attrs.setInteriorMaterial(Material.ORANGE);
                    }
                    else if(!a.isReal && a.adsbOutStatus){
                        attrs.setInteriorMaterial(Material.BLUE);
                    }
                    else if(a.isReal && !a.adsbOutStatus){
                        attrs.setInteriorMaterial(Material.GRAY);
                    }                    
                    else{
                        attrs.setInteriorMaterial(Material.WHITE);
                    }
                    ArrayList positions_top = new ArrayList();
                    double heading = Math.toRadians(a.heading);
                    positions_top.add(Position.fromDegrees(a.latitude+Math.cos(heading)*factor, a.longitude+Math.sin(heading)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_top.add(Position.fromDegrees(a.latitude+(Math.sin(heading)/2)*factor, a.longitude-(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_top.add(Position.fromDegrees(a.latitude-(Math.sin(heading)/2)*factor, a.longitude+(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    gov.nasa.worldwind.render.Polygon aircraft_top = new gov.nasa.worldwind.render.Polygon(positions_top);
                    aircraft_top.setAltitudeMode(WorldWind.ABSOLUTE);
                    aircraft_top.setAttributes(attrs);
                    aircraft_top.setVisible(true);
                    aircraft_top.setValue(AVKey.DISPLAY_NAME, a.callSign);
                    layer.addRenderable(aircraft_top);
                    ArrayList positions_below = new ArrayList();
                    positions_below.add(Position.fromDegrees(a.latitude+Math.cos(heading)*factor, a.longitude+Math.sin(heading)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    positions_below.add(Position.fromDegrees(a.latitude+(Math.sin(heading)/2)*factor, a.longitude-(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    positions_below.add(Position.fromDegrees(a.latitude-(Math.sin(heading)/2)*factor, a.longitude+(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    gov.nasa.worldwind.render.Polygon aircraft_below = new gov.nasa.worldwind.render.Polygon(positions_below);
                    aircraft_below.setAltitudeMode(WorldWind.ABSOLUTE);
                    aircraft_below.setAttributes(attrs);
                    aircraft_below.setVisible(true);
                    aircraft_below.setValue(AVKey.DISPLAY_NAME, a.callSign);
                    layer.addRenderable(aircraft_below);
                    ArrayList positions_side1 = new ArrayList();
                    positions_side1.add(Position.fromDegrees(a.latitude+Math.cos(heading)*factor, a.longitude+Math.sin(heading)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_side1.add(Position.fromDegrees(a.latitude+(Math.sin(heading)/2)*factor, a.longitude-(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_side1.add(Position.fromDegrees(a.latitude+(Math.sin(heading)/2)*factor, a.longitude-(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    positions_side1.add(Position.fromDegrees(a.latitude+Math.cos(heading)*factor, a.longitude+Math.sin(heading)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    gov.nasa.worldwind.render.Polygon aircraft_side1 = new gov.nasa.worldwind.render.Polygon(positions_side1);
                    aircraft_side1.setAltitudeMode(WorldWind.ABSOLUTE);
                    aircraft_side1.setAttributes(attrs);
                    aircraft_side1.setVisible(true);
                    aircraft_side1.setValue(AVKey.DISPLAY_NAME, a.callSign);
                    layer.addRenderable(aircraft_side1);
                    ArrayList positions_side2 = new ArrayList();
                    positions_side2.add(Position.fromDegrees(a.latitude+Math.cos(heading)*factor, a.longitude+Math.sin(heading)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_side2.add(Position.fromDegrees(a.latitude-(Math.sin(heading)/2)*factor, a.longitude+(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_side2.add(Position.fromDegrees(a.latitude-(Math.sin(heading)/2)*factor, a.longitude+(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    positions_side2.add(Position.fromDegrees(a.latitude+Math.cos(heading)*factor, a.longitude+Math.sin(heading)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    gov.nasa.worldwind.render.Polygon aircraft_side2 = new gov.nasa.worldwind.render.Polygon(positions_side2);
                    aircraft_side2.setAltitudeMode(WorldWind.ABSOLUTE);
                    aircraft_side2.setAttributes(attrs);
                    aircraft_side2.setVisible(true);
                    aircraft_side2.setValue(AVKey.DISPLAY_NAME, a.callSign);
                    layer.addRenderable(aircraft_side2);
                    ArrayList positions_side3 = new ArrayList();
                    positions_side3.add(Position.fromDegrees(a.latitude+(Math.sin(heading)/2)*factor, a.longitude-(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_side3.add(Position.fromDegrees(a.latitude-(Math.sin(heading)/2)*factor, a.longitude+(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude+height/2));
                    positions_side3.add(Position.fromDegrees(a.latitude-(Math.sin(heading)/2)*factor, a.longitude+(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    positions_side3.add(Position.fromDegrees(a.latitude+(Math.sin(heading)/2)*factor, a.longitude-(Math.cos(heading)/2)*factor/Math.cos(Math.toRadians(a.latitude)), a.altitude-height/2));
                    gov.nasa.worldwind.render.Polygon aircraft_side3 = new gov.nasa.worldwind.render.Polygon(positions_side3);
                    aircraft_side3.setAltitudeMode(WorldWind.ABSOLUTE);
                    aircraft_side3.setAttributes(attrs);
                    aircraft_side3.setVisible(true);
                    aircraft_side3.setValue(AVKey.DISPLAY_NAME, a.callSign);
                    layer.addRenderable(aircraft_side3);

                    if(t >= separation && t < 2*separation){
                        drawSquare(layer, t-separation, attrs, aircrafts.get(t-separation).aircraftsT.get(i));
                    }
                    else if(t >= 2*separation && t < 3*separation){
                        drawSquare(layer, t-2*separation, attrs, aircrafts.get(t-2*separation).aircraftsT.get(i));
                        drawSquare(layer, t-separation, attrs, aircrafts.get(t-separation).aircraftsT.get(i));
                    }
                    else if(t >= 3*separation && t < 4*separation){
                        drawSquare(layer, t-3*separation, attrs, aircrafts.get(t-3*separation).aircraftsT.get(i));
                        drawSquare(layer, t-2*separation, attrs, aircrafts.get(t-2*separation).aircraftsT.get(i));
                        drawSquare(layer, t-separation, attrs, aircrafts.get(t-separation).aircraftsT.get(i));
                    }
                    else if(t >= 4*separation){
                        drawSquare(layer, t-4*separation, attrs, aircrafts.get(t-4*separation).aircraftsT.get(i));
                        drawSquare(layer, t-3*separation, attrs, aircrafts.get(t-3*separation).aircraftsT.get(i));
                        drawSquare(layer, t-2*separation, attrs, aircrafts.get(t-2*separation).aircraftsT.get(i));
                        drawSquare(layer, t-separation, attrs, aircrafts.get(t-separation).aircraftsT.get(i));
                    }
                }
                i += 1;
            }
            for (Position position : explosions){
                ShapeAttributes attrs = new BasicShapeAttributes();
                attrs.setInteriorOpacity(1);
                attrs.setEnableLighting(true);
                attrs.setOutlineMaterial(Material.BLACK);
                attrs.setOutlineWidth(2d);
                attrs.setDrawInterior(true);
                attrs.setDrawOutline(true);
                attrs.setInteriorMaterial(Material.RED);
                drawExplosion(layer, attrs, position);
            }
        }
        
        public AppFrame() throws IOException
        {          
            super(true, true, false);
            
            initAircrafts();
            
            //Create the layer where you will place your polygons
            RenderableLayer layer = new RenderableLayer();
            
            JPanel controlPanel = new JPanel();
            JPanel timePanel = new JPanel(new GridLayout(0, 1, 0, 0));
            timePanel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));
            timePanel.add(new JLabel("Time:"));
            JSlider timeSlider = new JSlider(0, aircrafts.size(), 0);
            timeSlider.addChangeListener((ChangeEvent event) -> {
                layer.removeAllRenderables();
                draw(layer, timeSlider.getValue());
                getWwd().redraw();
            });
            
            timePanel.add(timeSlider);
            controlPanel.add(timePanel);
            
            this.getControlPanel().add(controlPanel, BorderLayout.SOUTH);
            
            //Enable shape dragging, if you want.
            this.getWwd().addSelectListener(new BasicDragger(this.getWwd()));
            
            WorldWindow wwd = this.getWwd();
            
            this.getWwd().addPositionListener(new PositionListener() {
                @Override
                public void moved(PositionEvent event) {
                    factor = wwd.getView().getCurrentEyePosition().getAltitude()/9000000;
//                    factor = wwd.getView().getFieldOfView().getRadians();
//                    factor = wwd.getView().getViewport().height/300;
                    height = 60*1852*0.33*factor;
                    separation = (int) Math.floor(wwd.getView().getCurrentEyePosition().getAltitude()/8000);
                    layer.removeAllRenderables();
                    draw(layer, timeSlider.getValue());
                    getWwd().redraw();
                }
            });
                        
            draw(layer, t);
            
            insertBeforeCompass(this.getWwd(), layer);
            
            this.tabbedPane = new JTabbedPane();

            this.tabbedPane.add(new JPanel());
            this.tabbedPane.setTitleAt(0, "+");
            this.tabbedPane.addChangeListener(new ChangeListener()
            {
                public void stateChanged(ChangeEvent changeEvent)
                {
                    if (tabbedPane.getSelectedIndex() != 0)
                    {
                        previousTabIndex = tabbedPane.getSelectedIndex();
                        return;
                    }

                    String server = JOptionPane.showInputDialog("Enter wms server URL");
                    if (server == null || server.length() < 1)
                    {
                        tabbedPane.setSelectedIndex(previousTabIndex);
                        return;
                    }

                    // Respond by adding a new WMSLayerPanel to the tabbed pane.
                    if (addTab(tabbedPane.getTabCount(), server.trim()) != null)
                        tabbedPane.setSelectedIndex(tabbedPane.getTabCount() - 1);
                }
            });

            // Create a tab for each server and add it to the tabbed panel.
            for (int i = 0; i < servers.length; i++)
            {
                this.addTab(i + 1, servers[i]); // i+1 to place all server tabs to the right of the Add Server tab
            }

            // Display the first server pane by default.
            this.tabbedPane.setSelectedIndex(this.tabbedPane.getTabCount() > 0 ? 1 : 0);
            this.previousTabIndex = this.tabbedPane.getSelectedIndex();

            // Add the tabbed pane to a frame separate from the WorldWindow.
            JFrame controlFrame = new JFrame();
            controlFrame.getContentPane().add(tabbedPane);
            controlFrame.pack();
            controlFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            controlFrame.setVisible(true);
        }

        protected WMSLayersPanel addTab(int position, String server)
        {
            // Add a server to the tabbed dialog.
            try
            {
                WMSLayersPanel layersPanel = new WMSLayersPanel(AppFrame.this.getWwd(), server, wmsPanelSize);
                this.tabbedPane.add(layersPanel, BorderLayout.CENTER);
                String title = layersPanel.getServerDisplayString();
                this.tabbedPane.setTitleAt(position, title != null && title.length() > 0 ? title : server);

                return layersPanel;
            }
            catch (URISyntaxException e)
            {
                JOptionPane.showMessageDialog(null, "Server URL is invalid", "Invalid Server URL",
                    JOptionPane.ERROR_MESSAGE);
                tabbedPane.setSelectedIndex(previousTabIndex);
                return null;
            }
        }
    }

    public static void main(String[] args)
    {
        ApplicationTemplate.start("WorldWind WMS Layers", AppFrame.class);
    }
}