/*
 * SPDX-FileCopyrightText: 2026
 * SPDX-License-Identifier: Apache-2.0
 */

package org.lineageos.settings.chargespeed;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;

public class ChargingSpeedActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        overridePendingTransition(0, 0);

        if (!CoolDownUtils.isSupported()) {
            finish();
            return;
        }

        String[] entries = getResources().getStringArray(R.array.charging_speed_entries);
        String[] valuesStr = getResources().getStringArray(R.array.charging_speed_values);
        
        int saved = CoolDownUtils.loadSaved(this);
        int selectedIndex = 0;
        for (int i = 0; i < valuesStr.length; i++) {
            if (String.valueOf(saved).equals(valuesStr[i])) {
                selectedIndex = i;
                break;
            }
        }

        new AlertDialog.Builder(this)
                .setTitle(R.string.charging_speed_dialog_title)
                .setSingleChoiceItems(entries, selectedIndex, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        try {
                            int level = Integer.parseInt(valuesStr[which]);
                            CoolDownUtils.saveAndApply(ChargingSpeedActivity.this, level);
                        } catch (NumberFormatException ignored) {
                        }
                        dialog.dismiss();
                    }
                })
                .setOnDismissListener(new DialogInterface.OnDismissListener() {
                    @Override
                    public void onDismiss(DialogInterface dialog) {
                        finish();
                    }
                })
                .show();
    }

    @Override
    public void finish() {
        super.finish();
        overridePendingTransition(0, 0);
    }
}
