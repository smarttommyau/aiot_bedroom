package com.tommy.AIotFlirCameraConnector;

import android.util.Log;

import com.flir.flironesdk.RenderedImage;

import java.net.Socket;
import java.util.HashSet;
import java.util.Hashtable;

public class FullFrameManager {
    private Hashtable<Integer,FullFrame> table;
    private HashSet<Integer> hashes;
    //Integer is the hash value
    private Socket socketstream = null;
    private volatile int valid_count;
    public FullFrameManager(Socket socket){
        socketstream = socket;
        table = new Hashtable<Integer,FullFrame>();
        hashes = new HashSet<Integer>();
        valid_count = 0;
    }
    public void add(final RenderedImage frame){
        Integer hash = frame.getFrame().hashCode();
        Log.i("Socket","Hash:" + hash.toString());
        Log.i("Socket:Hashtable", String.valueOf(table.size()));

        FullFrame fullFrame = (FullFrame) table.get(hash);
        if(hashes.contains(hash)){
            hashes.remove(hash);
            return;
        }
        if(fullFrame == null){
            if (valid_count>=3){
                hashes.add(hash);
                return;
            }else {
                fullFrame = new FullFrame(socketstream, this, hash);
                table.put(hash,fullFrame);
                valid_count++;
            }
        }
        if (frame.imageType() == RenderedImage.ImageType.VisibleAlignedRGBA8888Image) {
            fullFrame.Visual(frame);
        } else if (frame.imageType() == RenderedImage.ImageType.ThermalRadiometricKelvinImage) {
            fullFrame.Thermal(frame);
        }
    }
    public void finish(Integer Hash){
        table.remove(Hash);
        valid_count--;
    }
}
