package com.flir.flironeexampleapplication;

import android.content.Context;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import com.flir.flironesdk.RenderedImage;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class SocketConnection {
    private final String ip;
    private final int port;
    private final Context context;
    public boolean success;
    private Socket socket;
    private BufferedReader br;
    private volatile boolean socketlock;
    public SocketConnection(final String ip, final int port, final Context context) throws IOException, InterruptedException {
        this.ip = ip;
        this.port = port;
        this.context = context;
        this.success = true;
        this.socket = null;
        this.socketlock = true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    socket = new Socket(InetAddress.getByName(ip), port);
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
                InputStream is = null;
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
                br = new BufferedReader(isr);
                String result = null;
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
                socketlock = false;
                Looper.prepare();
                Toast.makeText(context,"Update success",Toast.LENGTH_SHORT).show();
                Looper.loop();
            }
        }).start();
        //initial finished
    }
    public void sendFrame(final RenderedImage frame) throws IOException, InterruptedException {
        if(this.socketlock)
            return;
        this.socketlock = true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                OutputStream outputStream = null;
                try {
                    outputStream = socket.getOutputStream();
                } catch (IOException e) {
                    Log.e("SocketInfo",e.toString());
                    Toast.makeText(context,e.toString(),Toast.LENGTH_SHORT).show();
                    throw new RuntimeException(e);
                }
                byte[] data = frame.pixelData();
                //send the size of the frame
                Log.i( "SocketInfo","size:"+data.length);
                String result="";
                try {
                    outputStream.write((""+data.length).getBytes(StandardCharsets.US_ASCII));
                    outputStream.flush();
                    Log.i( "SocketInfo","size confirmation: "+br.readLine());
                    //send
                    outputStream.write(data);
                    outputStream.flush();
                    Log.i("SocketInfo","sent");
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
    public void terminate() throws InterruptedException {
        socketlock = true;
            Thread t1 = new Thread(new Runnable() {
                @Override
                public void run() {
                    if(socket.isConnected()&&!socket.isClosed()) {
                        try {
                            socket.close();
                        } catch (IOException e) {
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
