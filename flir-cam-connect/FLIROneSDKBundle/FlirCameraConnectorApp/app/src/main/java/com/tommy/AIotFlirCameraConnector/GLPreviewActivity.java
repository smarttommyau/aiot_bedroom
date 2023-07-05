package com.tommy.AIotFlirCameraConnector;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
//import android.graphics.Bitmap;
import android.opengl.GLSurfaceView;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.PermissionChecker;
import android.util.Log;
import android.view.OrientationEventListener;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import com.flir.flironesdk.Device;
import com.flir.flironesdk.Frame;
import com.flir.flironesdk.FrameProcessor;
import com.flir.flironesdk.RenderedImage;

//import java.io.BufferedInputStream;
//import java.io.ByteArrayOutputStream;
//import java.io.File;
//import java.io.FileInputStream;
//import java.io.FileNotFoundException;
//import java.io.IOException;
//import java.io.OutputStream;
//import java.nio.ByteBuffer;
import java.net.InetSocketAddress;
import java.text.NumberFormat;
import java.util.EnumSet;

import java.net.Socket;
// FIXME: urgent fix to drop frames when there is already too much frames in the queue

public class GLPreviewActivity extends Activity implements Device.Delegate, FrameProcessor.Delegate, Device.StreamDelegate{
    GLSurfaceView thermalSurfaceView;
//    private volatile boolean imageCaptureRequested = false;
    private boolean chargeCableIsConnected = true;

    private int deviceRotation= 0;
    private OrientationEventListener orientationEventListener;


    private volatile Device flirOneDevice;
    private FrameProcessor frameProcessor;

//    private String lastSavedPath;


    private Device.TuningState currentTuningState = Device.TuningState.Unknown;
    // Device Delegate methods

    // Called during device discovery, when a device is connected
    // During this callback, you should save a reference to device
    // You should also set the power update delegate for the device if you have one
    // Go ahead and start frame stream as soon as connected, in this use case
    // Finally we create a frame processor for rendering frames

    //Socket variables
    private volatile String ip;
    private volatile int port;
    private volatile Socket StreamSocket = null;
    private volatile boolean socketsetup = false;
    private volatile FullFrameManager fullframemanager = null;
    //    private volatile SocketConnection socketConnection;
//    private volatile SocketConnection socketConnectionTh;
//    private volatile int frameid;
//    private volatile int curV;
//    private volatile int curT;

    public void onDeviceConnected(Device device){
        Log.i("ExampleApp", "Device connected!");
        runOnUiThread(new Runnable() {
                          @Override
                          public void run() {
                              findViewById(R.id.pleaseConnect).setVisibility(View.GONE);
                          }
                      });
        
        flirOneDevice = device;
        flirOneDevice.startFrameStream(this);
        orientationEventListener.enable();

    }


    /**
     * Indicate to the user that the device has disconnected
     */
    public void onDeviceDisconnected(Device device){
        Log.i("ExampleApp", "Device disconnected!");

        final ToggleButton chargeCableButton = (ToggleButton)findViewById(R.id.chargeCableToggle);
        final TextView levelTextView = (TextView)findViewById(R.id.batteryLevelTextView);
        final ImageView chargingIndicator = (ImageView)findViewById(R.id.batteryChargeIndicator);
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                findViewById(R.id.pleaseConnect).setVisibility(View.GONE);
                levelTextView.setText("--");
                chargeCableButton.setChecked(chargeCableIsConnected);
                chargeCableButton.setVisibility(View.INVISIBLE);
                chargingIndicator.setVisibility(View.GONE);
                findViewById(R.id.tuningProgressBar).setVisibility(View.GONE);
                findViewById(R.id.tuningTextView).setVisibility(View.GONE);
                findViewById(R.id.connect_sim_button).setEnabled(true);
            }
        });
        flirOneDevice = null;
        orientationEventListener.disable();
    }

    /**
     * If using RenderedImage.ImageType.ThermalRadiometricKelvinImage, you should not rely on
     * the accuracy if tuningState is not Device.TuningState.Tuned
     * @param tuningState
     */
    public void onTuningStateChanged(Device.TuningState tuningState){
        Log.i("ExampleApp", "Tuning state changed changed!");

        currentTuningState = tuningState;
        if (tuningState == Device.TuningState.InProgress){
            runOnUiThread(new Thread(){
                @Override
                public void run() {
                    super.run();
                    findViewById(R.id.tuningProgressBar).setVisibility(View.VISIBLE);
                    findViewById(R.id.tuningTextView).setVisibility(View.VISIBLE);
                }
            });
        }else {
            runOnUiThread(new Thread() {
                @Override
                public void run() {
                    super.run();
                    findViewById(R.id.tuningProgressBar).setVisibility(View.GONE);
                    findViewById(R.id.tuningTextView).setVisibility(View.GONE);
                }
            });
        }
    }

    @Override
    public void onAutomaticTuningChanged(boolean deviceWillTuneAutomatically) {

    }

    // StreamDelegate method
    public void onFrameReceived(Frame frame) {
//        frameid++;
//        Log.v("ExampleApp", "Frame received!");

        if (currentTuningState != Device.TuningState.InProgress){
            frameProcessor.processFrame(frame, FrameProcessor.QueuingOption.CLEAR_QUEUED);
            thermalSurfaceView.requestRender();
//            if(this.socketConnection!= null && this.socketConnection.success){
//                try{
//                    this.socketConnection.sendFrame(frame,frameProcessor);
//                } catch (Exception e) {
//                    e.printStackTrace();
//                }
//            }
        }

    }

//    private Bitmap thermalBitmap = null;

    // Frame Processor Delegate method, will be called each time a rendered frame is produced
    public void onFrameProcessed(final RenderedImage renderedImage){
        if (StreamSocket != null && StreamSocket.isConnected() && !StreamSocket.isClosed() && socketsetup) {
            if (fullframemanager == null) {
                fullframemanager = new FullFrameManager(StreamSocket);
            }
            if (renderedImage.imageType() == RenderedImage.ImageType.VisibleAlignedRGBA8888Image || renderedImage.imageType() == RenderedImage.ImageType.ThermalRadiometricKelvinImage) {
                fullframemanager.add(renderedImage);
            }
        }
        if(StreamSocket != null && StreamSocket.isClosed()){
            Toast.makeText(getApplicationContext(),"Closing socket",Toast.LENGTH_SHORT);

            try {
                StreamSocket.close();
                socketsetup = false;
                fullframemanager = null;
                ((Button)findViewById(R.id.AdressUpdate)).setText("START");
            }catch (Exception ex) {
                Log.e("Socket","Close failed");
            }
        }
//        if(this.socketConnection!= null && this.socketConnection.success) {
//            new Thread(new Runnable() {
//                @Override
//                public void run() {
//                    if (renderedImage.imageType() == RenderedImage.ImageType.VisibleAlignedRGBA8888Image) {
//                        try {
//                            int cur = socketConnection.frameidd;
//                            if(socketConnection.sendrenderFrame(renderedImage,curT)){
//                                curV = cur;
//                            }
//                        } catch (Exception e) {
//                            e.printStackTrace();
//                        }
//                    } else if (renderedImage.imageType() == RenderedImage.ImageType.ThermalRadiometricKelvinImage) {
//
//                        try {
//                            if(socketConnectionTh!= null && socketConnectionTh.success) {
//                                int cur = socketConnectionTh.frameidd;
//                                if(socketConnectionTh.sendTemperaturedata(renderedImage,curV)){
//                                    curT = cur;
//                                }
//                            }
//                        } catch (Exception e) {
//                            e.printStackTrace();
//                        }
//                    }
//                }
//            }).start();
//
//        }
        if (renderedImage.imageType() == RenderedImage.ImageType.ThermalRadiometricKelvinImage){
            // Note: this code is not optimized
            int[] thermalPixels = renderedImage.thermalPixelValues();
            // average the center 9 pixels for the spot meter

            int width = renderedImage.width();
            int height = renderedImage.height();
            int centerPixelIndex = width * (height/2) + (width/2);
            int[] centerPixelIndexes = new int[] {
                    centerPixelIndex, centerPixelIndex-1, centerPixelIndex+1,
                    centerPixelIndex - width,
                    centerPixelIndex - width - 1,
                    centerPixelIndex - width + 1,
                    centerPixelIndex + width,
                    centerPixelIndex + width - 1,
                    centerPixelIndex + width + 1
            };

            double averageTemp = 0;

            for (int i = 0; i < centerPixelIndexes.length; i++){
                // Remember: all primitives are signed, we want the unsigned value,
                // we've used renderedImage.thermalPixelValues() to get unsigned values
                int pixelValue = (thermalPixels[centerPixelIndexes[i]]);
                averageTemp += (((double)pixelValue) - averageTemp) / ((double) i + 1);
            }
            double averageC = (averageTemp / 100) - 273.15;
            NumberFormat numberFormat = NumberFormat.getInstance();
            numberFormat.setMaximumFractionDigits(2);
            numberFormat.setMinimumFractionDigits(2);
            final String spotMeterValue = numberFormat.format(averageC) + "ºC";
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    ((TextView)findViewById(R.id.spotMeterValue)).setText(spotMeterValue);
                }
            });

        }
}
    public void onTuneClicked(View v){
        if (flirOneDevice != null){
            flirOneDevice.performTuning();
        }

    }

    @Override
    protected void onStart(){
        super.onStart();
        try {
            Device.startDiscovery(this, this);
        }catch(IllegalStateException e){
            // it's okay if we've already started discovery
        }catch (SecurityException e){
            // On some platforms, we need the user to select the app to give us permisison to the USB device.
            Toast.makeText(this, "Please insert FLIR One and select "+getString(R.string.app_name), Toast.LENGTH_LONG).show();
            // There is likely a cleaner way to recover, but for now, exit the activity and
            // wait for user to follow the instructions;
            finish();
        }
    }

    ScaleGestureDetector mScaleDetector;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

//        if (android.os.Build.VERSION.SDK_INT > 9) {
//            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
//            StrictMode.setThreadPolicy(policy);
//        }

        setContentView(R.layout.activity_gl_preview);

//        final View controlsView = findViewById(R.id.fullscreen_content_controls);
//        final View controlsViewTop = findViewById(R.id.fullscreen_content_controls_top);
//        final View contentView = findViewById(R.id.fullscreen_content);

//        frameProcessor = new FrameProcessor(this, this, EnumSet.of(RenderedImage.ImageType.VisibleAlignedRGBA8888Image,RenderedImage.ImageType.ThermalRadiometricKelvinImage, RenderedImage.ImageType.ThermalRGBA8888Image), true);
        frameProcessor = new FrameProcessor(this, this, EnumSet.of(RenderedImage.ImageType.VisibleAlignedRGBA8888Image,RenderedImage.ImageType.ThermalRadiometricKelvinImage), true);
        frameProcessor.setImagePalette(RenderedImage.Palette.Rainbow);
        frameProcessor.setGLOutputMode(RenderedImage.ImageType.VisibleAlignedRGBA8888Image);
        thermalSurfaceView = (GLSurfaceView) findViewById(R.id.imageView);
        thermalSurfaceView.setPreserveEGLContextOnPause(true);
        thermalSurfaceView.setEGLContextClientVersion(2);
        thermalSurfaceView.setRenderer(frameProcessor);
        thermalSurfaceView.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
//        thermalSurfaceView.setDebugFlags(GLSurfaceView.DEBUG_CHECK_GL_ERROR | GLSurfaceView.DEBUG_LOG_GL_CALLS);


//        final String[] imageTypeNames = new String[]{ "Visible", "Thermal", "MSX" };
//        final RenderedImage.ImageType[] imageTypeValues = new RenderedImage.ImageType[]{
//                RenderedImage.ImageType.VisibleAlignedRGBA8888Image,
//                RenderedImage.ImageType.ThermalRGBA8888Image,
//                RenderedImage.ImageType.BlendedMSXRGBA8888Image,
//        };


        //Setup socket update button
        ((Button)findViewById(R.id.AdressUpdate)).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //initial socket connection with pc
                ip = ((EditText) findViewById(R.id.Adress)).getText().toString();
                port = Integer.parseInt(((EditText)findViewById(R.id.port)).getText().toString());
                Log.i("convert",ip+":"+port);
                if (StreamSocket == null || StreamSocket.isClosed()) {
                    Toast.makeText(getApplicationContext(),"Opening socket",Toast.LENGTH_SHORT);
                    new Thread(new Runnable() {
                        @Override
                        public void run() {
                            try {
                                StreamSocket = new Socket();
                                StreamSocket.connect(new InetSocketAddress(ip, port), 500);
                                byte[] accept = new byte[20];
                                StreamSocket.getInputStream().read(accept);
                                Log.i("Socket",new String(accept));
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        ((Button) findViewById(R.id.AdressUpdate)).setText("STOP");
                                    }
                                });
                                socketsetup = true;
                            } catch (Exception e) {
                                Log.e("Socket", e.toString());
                            }
                        }
                    }).start();
                }else{
                    Toast.makeText(getApplicationContext(),"Closing socket",Toast.LENGTH_SHORT);

                    try {
                        StreamSocket.close();
                        socketsetup = false;
                        fullframemanager = null;
                        ((Button)findViewById(R.id.AdressUpdate)).setText("START");
                    }catch (Exception ex) {
                        Log.e("Socket","Close failed");
                    }

                }
//                if(socketConnection != null) {
//                    try {
//                        socketConnection.terminate();
//                    } catch (InterruptedException e) {
//                        throw new RuntimeException(e);
//                    }
//                }
//
//                try {
//                    socketConnection = new SocketConnection(ip,port,GLPreviewActivity.this);
//                    socketConnectionTh = new SocketConnection(ip,port,GLPreviewActivity.this);
//                    socketConnection.setup(true);
//                    socketConnectionTh.setup(false);
//                    if(socketConnection.success == false)
//                        socketConnection = null;
//                    if(socketConnectionTh.success == false)
//                        socketConnectionTh = null;
//                } catch (Exception e) {
//                    e.printStackTrace();
//                }
//                frameid = 0;
            }
        });

        // Upon interacting with UI controls, delay any scheduled hide()
        // operations to prevent the jarring behavior of controls going away
        // while interacting with the UI.
//        findViewById(R.id.change_view_button).setOnTouchListener(mDelayHideTouchListener);


        orientationEventListener = new OrientationEventListener(this) {
            @Override
            public void onOrientationChanged(int orientation) {
                deviceRotation = orientation;
            }
        };
        mScaleDetector = new ScaleGestureDetector(this, new ScaleGestureDetector.OnScaleGestureListener() {
            @Override
            public void onScaleEnd(ScaleGestureDetector detector) {
            }
            @Override
            public boolean onScaleBegin(ScaleGestureDetector detector) {
                return true;
            }
            @Override
            public boolean onScale(ScaleGestureDetector detector) {
                Log.d("ZOOM", "zoom ongoing, scale: " + detector.getScaleFactor());
                frameProcessor.setMSXDistance(detector.getScaleFactor());
                return false;
            }
        });

//        findViewById(R.id.fullscreen_content).setOnTouchListener(new View.OnTouchListener() {
//            @Override
//            public boolean onTouch(View v, MotionEvent event) {
//                mScaleDetector.onTouchEvent(event);
//                return true;
//            }
//        });

        String cameraPermission = Manifest.permission.CAMERA;
        boolean permissionGranted = false;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            permissionGranted = (ContextCompat.checkSelfPermission(this, cameraPermission) == PackageManager.PERMISSION_GRANTED);
        }
        else {
            permissionGranted = (PermissionChecker.checkSelfPermission(this, cameraPermission) == PermissionChecker.PERMISSION_GRANTED);
        }

        if(!permissionGranted) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(this, cameraPermission)) {
                Toast.makeText(this, "App requires camera permission", Toast.LENGTH_LONG).show();
            }
            else {
                ActivityCompat.requestPermissions(this, new String[]{cameraPermission}, 0);
            }
        }
    }

    @Override
    public void onPause(){
        super.onPause();

        thermalSurfaceView.onPause();
        if (flirOneDevice != null){
            flirOneDevice.stopFrameStream();
        }
    }
    @Override
    public void onResume(){
        super.onResume();

        thermalSurfaceView.onResume();

        if (flirOneDevice != null){
            flirOneDevice.startFrameStream(this);
        }
    }
    @Override
    public void onStop() {
        // We must unregister our usb receiver, otherwise we will steal events from other apps
        Log.e("PreviewActivity", "onStop, stopping discovery!");
        Device.stopDiscovery();
        flirOneDevice = null;
        super.onStop();
    }

}
