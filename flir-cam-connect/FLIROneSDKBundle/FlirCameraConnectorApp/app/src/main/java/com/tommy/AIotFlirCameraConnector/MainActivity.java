package com.tommy.AIotFlirCameraConnector;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {

    public static final int PERM_REQUEST_CAPTURE_CODE = 100;
    public static final String[] PERM_REQUEST_CAPTURE_STRING = new String[] {
            Manifest.permission.CAMERA
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void onStartButtonClicked(View view) {
        if(!hasCameraPermission()) {
            requestCameraPermissions();
        }
        else {
            startThermalCaptureActivity();
        }
    }

    private void startThermalCaptureActivity() {
        Intent intent = new Intent(this, GLPreviewActivity.class);
        startActivity(intent);
    }

    private void requestCameraPermissions() {
        if (ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)) {
            ActivityCompat.requestPermissions(this, PERM_REQUEST_CAPTURE_STRING, PERM_REQUEST_CAPTURE_CODE);
        }
        else {
            ActivityCompat.requestPermissions(this, PERM_REQUEST_CAPTURE_STRING, PERM_REQUEST_CAPTURE_CODE);
        }
    }

    private boolean hasCameraPermission() {
        int perm1 = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA);
        int perm2 = ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE);
        return PackageManager.PERMISSION_GRANTED == perm1 && PackageManager.PERMISSION_GRANTED == perm2;
    }


    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String permissions[], @NonNull int[] grantResults) {
        switch (requestCode) {
            case PERM_REQUEST_CAPTURE_CODE: {
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    startThermalCaptureActivity();
                }
                else {
                    Toast.makeText(this, "Camera permissions are needed for thermal capture", Toast.LENGTH_SHORT).show();
                }

                return;
            }
            default: {
                break;
            }
        }
    }
}
