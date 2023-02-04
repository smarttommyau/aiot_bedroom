package com.tommy.AIotFlirCameraConnector;

import android.content.Context;
import android.graphics.Bitmap;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import com.flir.flironesdk.Frame;
import com.flir.flironesdk.FrameProcessor;
import com.flir.flironesdk.RenderedImage;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ConnectException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class SocketConnection {
    private final Context context;
    public boolean success;
    private Socket socket;
    private volatile boolean socketlock;
//    private volatile boolean lastlock;//true for visual , false for thermal
//    private volatile boolean lastlocklock;
//    private volatile boolean first;
    private volatile boolean forcestop;
    public volatile int frameidd;
    private volatile boolean setup;
    public SocketConnection(final String ip, final int port, final Context context) {
        this.context = context;
        this.success = true;
        this.socket = null;
        this.socketlock = true;
        this.frameidd = 0;
        this.setup = false;
//        this.lastlocklock = false;
//        this.lastlock = false;
//        this.first = true;
        this.forcestop = false;
        final Thread t1 = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    socket = new Socket();
                    socket.connect(new InetSocketAddress(ip,port),500);
                    Log.i("SocketInfo",ip+":"+port+" connecting+");
                }catch(Exception e){
                    Log.e("SocketInfo",e.toString());
                    Looper.prepare();
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    Looper.loop();
                    success = false;
                    throw new RuntimeException(e);
                }
                if(!success) {
                    return;
                }
                socket.isConnected();
                InputStream is;
                try {
                    is = socket.getInputStream();
                } catch (IOException e) {
                    Log.e("SocketInfo",e.toString());
                    Looper.prepare();
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    Looper.loop();
                    success = false;
                    throw new RuntimeException(e);
                }
                InputStreamReader isr = new InputStreamReader(is);
                BufferedReader br = new BufferedReader(isr);
                String result = "r";
                try {
                    result = br.readLine();
                } catch (IOException e) {
                    Log.e("SocketInfo",e.toString());
                    Looper.prepare();
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    Looper.loop();

                    success = false;
                    throw new RuntimeException(e);
                }
                if(result.charAt(0) == 'r'){//check if connection accepted
                    Looper.prepare();
                    Toast.makeText(context,"connection rejected",Toast.LENGTH_SHORT).show();
                    Looper.loop();

                    success = false;
                    try {
                        socket.close();
                    } catch (IOException e) {

                        Log.e("SocketInfo",e.toString());
                        Looper.prepare();
                        Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                        Looper.loop();
                        success = false;
                        throw new RuntimeException(e);
                    }
                }
                setup = true;
                Looper.prepare();
                Toast.makeText(context,"Update success",Toast.LENGTH_SHORT).show();
                Looper.loop();
            }
        });
        t1.start();

        //initial finished
    }
    public void setup(final Boolean VisualQ){
        new Thread(new Runnable() {
            @Override
            public void run() {
                Log.i("SocketInfo","callsetup");
                while(!setup&&success)
                    ;
                if(!success){
                    Log.e("SocketInfo","setup cannot run as success is false");
                    return;
                }
                Log.i("SocketInfo","startsetup");
                OutputStream outputStream;
                BufferedReader br;
                try {
                    outputStream = socket.getOutputStream();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                } catch (IOException e) {
                    Log.e("SocketInfo", e.toString());
                    Toast.makeText(context, e.toString(), Toast.LENGTH_SHORT).show();
                    throw new RuntimeException(e);
                }
                Log.i("SocketInfo","setup socket");
                try {
                    if(VisualQ) {
                        outputStream.write("true".getBytes(StandardCharsets.US_ASCII));
                    }else{
                        outputStream.write("false".getBytes(StandardCharsets.US_ASCII));
                    }
                    outputStream.flush();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                try {
                    Log.i("SocketInfo",br.readLine());
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            socketlock = false;
            }
        }).start();

    }
    public void sendFrame(final Frame frame, final FrameProcessor frameProcessor){
        if(this.socketlock)
            return;
        this.socketlock = true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                OutputStream outputStream;
                BufferedReader br;
                try {
                    outputStream = socket.getOutputStream();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                } catch (IOException e) {
                    Log.e("SocketInfo",e.toString());
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    throw new RuntimeException(e);
                }
//                byte[] data = frame.pixelData();

                File file;
                try {
                    file = File.createTempFile("temp","temp");
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                try {
                    frame.save(file,frameProcessor);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                byte[] data = new byte[(int) file.length()];
                try {
                    BufferedInputStream buf = new BufferedInputStream(new FileInputStream(file));
                    buf.read(data,0, data.length);
                    buf.close();
                } catch (FileNotFoundException e) {
                    throw new RuntimeException(e);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                //send the size of the frame
                Log.i( "SocketInfo","size:"+data.length);
                String result;
                try {
                    Log.i("SocketInfo","sending new");
                    outputStream.write(("new".getBytes(StandardCharsets.US_ASCII)));
                    outputStream.flush();
                    Log.i( "SocketInfo","Connection confirmation: "+br.readLine());
                    outputStream = socket.getOutputStream();
                    outputStream.write(((""+data.length).getBytes(StandardCharsets.US_ASCII)));
                    outputStream.flush();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    Log.i( "SocketInfo","size confirmation: "+br.readLine());
                    //send
                    outputStream = socket.getOutputStream();
                    outputStream.write(data);
                    outputStream.flush();
                    Log.i("SocketInfo","sent");
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    result = br.readLine();
                    Log.i("SocketInfo",result);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }

                if(result.charAt(0) != 'a')
                    Log.e( "SocketInfo",result);
                else
                    Log.i("SocketInfo",result);
                socketlock = false;
            }

        }).start();
    }
    public boolean sendrenderFrame(final RenderedImage frame,int cur){
        final int frameid = this.frameidd;
        this.frameidd++;
        if(frameid==cur)
           while (this.socketlock)
               ;
 //        final boolean currentlock = frame.imageType()==RenderedImage.ImageType.VisibleAlignedRGBA8888Image;
        if(this.socketlock||frameid<cur/*&&(this.lastlocklock||currentlock==this.lastlock)*/)
            return false;
        Log.i("Socket send type", "Visual"+frameid);

//        else {
//            if(this.first){
//                this.first = false;
//            }
//            this.lastlocklock = true;
//            while (this.socketlock)
//                ;
//            lastlock = frame.imageType()== RenderedImage.ImageType.VisibleAlignedRGBA8888Image;
//            this.socketlock = true;
//            this.lastlocklock = false;
//        }
        this.socketlock = true;
//        lastlock = frame.imageType()== RenderedImage.ImageType.VisibleAlignedRGBA8888Image;

        new Thread(new Runnable() {
            @Override
            public void run() {
                OutputStream outputStream;
                BufferedReader br;
                try {
                    outputStream = socket.getOutputStream();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                } catch (IOException e) {
                    Log.e("SocketInfo",e.toString());
                    Looper.prepare();
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    Looper.loop();
                    throw new RuntimeException(e);
                }
                Bitmap bitmap = frame.getBitmap();
                ByteArrayOutputStream stream = new ByteArrayOutputStream();
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream);
                byte[] data = stream.toByteArray();

                //send the size of the frame
                Log.i( "SocketInfo","size:"+data.length);
                String result;
                try {
                    Log.i("SocketInfo","sending new");
                    outputStream.write((("new "+frameid).getBytes(StandardCharsets.US_ASCII)));

                    outputStream.flush();
                    Log.i( "SocketInfo","Connection confirmation: "+br.readLine());
                    outputStream = socket.getOutputStream();
                    outputStream.write(((""+data.length).getBytes(StandardCharsets.US_ASCII)));
                    outputStream.flush();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    Log.i( "SocketInfo","size confirmation: "+br.readLine());
                    //send
                    outputStream = socket.getOutputStream();
                    outputStream.write(data);
                    outputStream.flush();
                    Log.i("SocketInfo","sent");
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    result = br.readLine();
                    Log.i("SocketInfo",result);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }

                if(result.charAt(0) != 'a')
                    Log.e( "SocketInfo",result);
                else
                    Log.i("SocketInfo",result);
                socketlock = false;
            }
        }).start();
        return true;
    }
    public boolean sendTemperaturedata(final RenderedImage frame,int cur){
        final int frameid = this.frameidd;
        this.frameidd++;
        if(frameid==cur)
            while (this.socketlock)
                ;
//        final boolean currentlock = frame.imageType()==RenderedImage.ImageType.VisibleAlignedRGBA8888Image;
        if(this.socketlock||frameid!=cur/*&&(currentlock==this.lastlock||this.lastlocklock)*/)
            return false;
        Log.i("Socket send type", "Thermal"+frameid);
//        else {
//            if(this.first) {
//                this.lastlocklock = true;
//                while (this.first)
//                    ;
//                this.lastlocklock = false;
//            }
//            this.lastlocklock = true;
//            while (this.socketlock)
//                ;
//            this.socketlock = true;
//            lastlock = frame.imageType()== RenderedImage.ImageType.VisibleAlignedRGBA8888Image;
//            this.lastlocklock = false;
//        }
        this.socketlock = true;
//        lastlock = frame.imageType()== RenderedImage.ImageType.VisibleAlignedRGBA8888Image;

        new Thread(new Runnable() {
            @Override
            public void run() {
                OutputStream outputStream;
                BufferedReader br;
                try {
                    outputStream = socket.getOutputStream();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                } catch (IOException e) {
                    Log.e("SocketInfo",e.toString());
                    Looper.prepare();
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    Looper.loop();
                    throw new RuntimeException(e);
                }
                short[] pixels = frame.thermalPixelData();
//                int[] pixels = frame.thermalPixelValues();
//                byte[] data = new byte[pixels.length*4];
//                for(int i=0;i<pixels.length;i++) {
//                    data[i*4] = (byte) (pixels[i] >> 24);
//                    data[i*4+1] = (byte) (pixels[i] >> 16);
//                    data[i*4+2] = (byte) (pixels[i] >> 8);
//                    data[i*4+3] = (byte) (pixels[i] /*>> 0*/);
//                }
                byte[] data = new byte[pixels.length*2];
                for(int i=0;i< pixels.length;i++){
                    data[i*2] = (byte)(pixels[i]>>8);
                    data[i*2+1] = (byte)(pixels[i]);
                }
                //send the size of the frame
                Log.i( "SocketInfo","size:"+data.length );
                String result;
                try {

                    Log.i("SocketInfo","sending new");
                    outputStream.write((("new "+ frameid).getBytes(StandardCharsets.US_ASCII)));
                    outputStream.flush();
                    Log.i( "SocketInfo","Connection confirmation: "+br.readLine());
                    outputStream = socket.getOutputStream();
                    outputStream.write(((""+data.length+" "+frame.width()+" "+frame.height()).getBytes(StandardCharsets.US_ASCII)));
                    outputStream.flush();
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    Log.i( "SocketInfo","size confirmation: "+br.readLine());
                    //send
                    outputStream = socket.getOutputStream();
                    outputStream.write(data);
                    outputStream.flush();
                    Log.i("SocketInfo","sent");
                    br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    result = br.readLine();
                    Log.i("SocketInfo",result);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }

                if(result.charAt(0) != 'a')
                    Log.e( "SocketInfo",result);
                else
                    Log.i("SocketInfo",result);
                socketlock = false;
            }

        }).start();
        return true;
    }
    public void terminate() throws InterruptedException {
        socketlock = true;
        forcestop = true;
            Thread t1 = new Thread(new Runnable() {
                @Override
                public void run() {
                    if(socket!=null&&socket.isConnected()&&!socket.isClosed()) {
                        try {
                            socket.close();
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        } catch (java.lang.NullPointerException e){
                            throw new RuntimeException(e);
                        }
                    }
                    socketlock = false;
                }
            });
            t1.start();
            t1.join();
    }
}
