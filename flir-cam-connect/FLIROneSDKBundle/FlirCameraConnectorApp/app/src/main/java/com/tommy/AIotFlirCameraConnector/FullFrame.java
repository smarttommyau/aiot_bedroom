package com.tommy.AIotFlirCameraConnector;

import android.graphics.Bitmap;
import android.util.Log;

import com.flir.flironesdk.RenderedImage;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.zip.Deflater;

public class FullFrame {
    private byte thermal[];
    private boolean thermalFin;
    private byte visual[];
    private boolean visualFin;

    private Socket streamSocket;
    public boolean died;

    private FullFrameManager FullFrameManager;
    public Integer hashcode;
    public FullFrame(Socket socket,FullFrameManager fullFrameManager,Integer hash) {
        thermal = null;
        visual = null;
        thermalFin = false;
        visualFin = false;
        streamSocket = socket;
        died = false;
        FullFrameManager = fullFrameManager;
        hashcode = hash;
    }

    public void Thermal(final RenderedImage frame) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                short[] pixels = frame.thermalPixelData();
                byte[] uncompressed_data = new byte[pixels.length * 2];
                for (int i = 0; i < pixels.length; i++) {
                    uncompressed_data[i * 2] = (byte) (pixels[i] >> 8);
                    uncompressed_data[i * 2 + 1] = (byte) (pixels[i]);
                }

                try {
                    thermal = compress(uncompressed_data, Deflater.DEFAULT_STRATEGY);
                    Log.i("Socket","thermal"+thermal.length);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                if(visualFin){
                    Log.i("socketthermvis","1xThermal:"+thermalFin+"Visualx"+visualFin);
                    StartSend();

                }else{
                    thermalFin = true;
                    Log.i("socketthermvis","1Thermal:"+thermalFin+"Visualx"+visualFin);

                }
            }
        }).start();
    }
    public void Visual(final RenderedImage frame) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                Bitmap bitmap = frame.getBitmap();
                ByteArrayOutputStream stream = new ByteArrayOutputStream();
//                ByteBuffer bytes = ByteBuffer.allocate(bitmap.getByteCount());
                Log.i("Compress","start");
                bitmap.compress(Bitmap.CompressFormat.WEBP, 100, stream);
                visual = stream.toByteArray();
//                bitmap.copyPixelsToBuffer(bytes);
//                visual = bytes.array();
                Log.i("Compress","end");

                Log.i("Socket","visual"+visual.length);
                if(thermalFin){
                    Log.i("socketthermvis","2xThermal:"+thermalFin+"Visualx"+visualFin);
                    StartSend();
                }else {
                    visualFin = true;
                    Log.i("socketthermvis","2Thermal:"+thermalFin+"Visualx"+visualFin);

                }
            }
        }).start();
    }
    public void StartSend(){
        if(!streamSocket.isConnected()||died){
            return;
        }
        died = true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                try{
                    // *2/8 to /4
                    final OutputStream outputStream = streamSocket.getOutputStream();
                    Log.i("Socket","sending");
                    byte[] send_data = ByteBuffer.allocate(Integer.SIZE  / 4 + thermal.length + visual.length).putInt(thermal.length).putInt(visual.length).put(thermal).put(visual).array();

                    synchronized (streamSocket) {
                        outputStream.write(send_data);
                        outputStream.flush();
                    }

                }catch(Exception e){
                    Log.e("Socket",e.toString());
                }
                FullFrameManager.finish(hashcode);

            }
        }).start();
    }

    private static byte[] compress(byte[] input, int compressionLevel) throws IOException {
        Deflater compressor = new Deflater(compressionLevel);
        compressor.setInput(input);
        compressor.finish();
        ByteArrayOutputStream bao = new ByteArrayOutputStream();
        byte[] readBuffer = new byte[1024];
        int readCount = 0;
        while (!compressor.finished()) {
            readCount = compressor.deflate(readBuffer);
            if (readCount > 0) {
                bao.write(readBuffer, 0, readCount);
            }
        }
        compressor.end();
        return bao.toByteArray();
    }
}
