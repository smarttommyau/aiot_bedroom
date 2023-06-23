package com.tommy.AIotFlirCameraConnector;

import android.util.Log;

import com.flir.flironesdk.RenderedImage;

import java.net.Socket;
import java.util.Hashtable;

public class FullFrameManager {
    Hashtable<Integer,FullFrame> table;
    //Integer is the hash value
    Socket socketstream = null;
    public FullFrameManager(Socket socket){
        socketstream = socket;
        table = new Hashtable<Integer,FullFrame>();
    }
    public void add(final RenderedImage frame){
        Integer hash = frame.getFrame().hashCode();
        Log.i("Socket","Hash:" + hash.toString());
        Log.i("Socket:Hashtable", String.valueOf(table.size()));
        FullFrame fullFrame = (FullFrame) table.get(hash);
        if(fullFrame == null){
            fullFrame = new FullFrame(socketstream);
            table.put(hash,fullFrame);
        }else{
            table.remove(hash);
        }
        if (frame.imageType() == RenderedImage.ImageType.VisibleAlignedRGBA8888Image) {
            fullFrame.Visual(frame);
        } else if (frame.imageType() == RenderedImage.ImageType.ThermalRadiometricKelvinImage) {
            fullFrame.Thermal(frame);
        }

    }
}
