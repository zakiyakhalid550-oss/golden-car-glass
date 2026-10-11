[35mapp.py[m[36m:[m[32m1206[m[36m:[m[1;31mdef verify_reset_otp[m():
[35mapp.py[m[36m-[m[32m1207[m[36m-[m
[35mapp.py[m[36m-[m[32m1208[m[36m-[m    if not session.get("reset_admin_id"):
[35mapp.py[m[36m-[m[32m1209[m[36m-[m        return redirect(url_for("forgot_password"))
[35mapp.py[m[36m-[m[32m1210[m[36m-[m
[35mapp.py[m[36m-[m[32m1211[m[36m-[m    if request.method == "POST":
[35mapp.py[m[36m-[m[32m1212[m[36m-[m
[35mapp.py[m[36m-[m[32m1213[m[36m-[m        entered_otp = request.form.get("otp", "").strip()
[35mapp.py[m[36m-[m[32m1214[m[36m-[m
[35mapp.py[m[36m-[m[32m1215[m[36m-[m        stored_otp = session.get("reset_otp")
[35mapp.py[m[36m-[m[32m1216[m[36m-[m        otp_expires = session.get("reset_otp_expires")
[35mapp.py[m[36m-[m[32m1217[m[36m-[m        attempts = session.get("reset_otp_attempts", 0)
[35mapp.py[m[36m-[m[32m1218[m[36m-[m
[35mapp.py[m[36m-[m[32m1219[m[36m-[m        if attempts >= 5:
[35mapp.py[m[36m-[m[32m1220[m[36m-[m            session.pop("reset_admin_id", None)
[35mapp.py[m[36m-[m[32m1221[m[36m-[m            session.pop("reset_email", None)
[35mapp.py[m[36m-[m[32m1222[m[36m-[m            session.pop("reset_otp", None)
[35mapp.py[m[36m-[m[32m1223[m[36m-[m            session.pop("reset_otp_expires", None)
[35mapp.py[m[36m-[m[32m1224[m[36m-[m            session.pop("reset_otp_attempts", None)
[35mapp.py[m[36m-[m[32m1225[m[36m-[m
[35mapp.py[m[36m-[m[32m1226[m[36m-[m            flash(
[35mapp.py[m[36m-[m[32m1227[m[36m-[m                "Too many incorrect attempts. Please request a new OTP.",
[35mapp.py[m[36m-[m[32m1228[m[36m-[m                "error"
[35mapp.py[m[36m-[m[32m1229[m[36m-[m            )
[35mapp.py[m[36m-[m[32m1230[m[36m-[m
[35mapp.py[m[36m-[m[32m1231[m[36m-[m            return redirect(url_for("forgot_password"))
[35mapp.py[m[36m-[m[32m1232[m[36m-[m
[35mapp.py[m[36m-[m[32m1233[m[36m-[m        if not otp_expires or time.time() > otp_expires:
[35mapp.py[m[36m-[m[32m1234[m[36m-[m            session.pop("reset_otp", None)
[35mapp.py[m[36m-[m[32m1235[m[36m-[m            session.pop("reset_otp_expires", None)
[35mapp.py[m[36m-[m[32m1236[m[36m-[m            session.pop("reset_otp_attempts", None)
[35mapp.py[m[36m-[m[32m1237[m[36m-[m
[35mapp.py[m[36m-[m[32m1238[m[36m-[m            flash(
[35mapp.py[m[36m-[m[32m1239[m[36m-[m                "OTP has expired. Please request a new OTP.",
[35mapp.py[m[36m-[m[32m1240[m[36m-[m                "error"
[35mapp.py[m[36m-[m[32m1241[m[36m-[m            )
[35mapp.py[m[36m-[m[32m1242[m[36m-[m
[35mapp.py[m[36m-[m[32m1243[m[36m-[m            return redirect(url_for("forgot_password"))
[35mapp.py[m[36m-[m[32m1244[m[36m-[m
[35mapp.py[m[36m-[m[32m1245[m[36m-[m        if not stored_otp or not secrets.compare_digest(entered_otp, stored_otp):
[35mapp.py[m[36m-[m[32m1246[m[36m-[m            session["reset_otp_attempts"] = attempts + 1
[35mapp.py[m[36m-[m[32m1247[m[36m-[m
[35mapp.py[m[36m-[m[32m1248[m[36m-[m            remaining = 4 - attempts
[35mapp.py[m[36m-[m[32m1249[m[36m-[m
[35mapp.py[m[36m-[m[32m1250[m[36m-[m            if remaining > 0:
[35mapp.py[m[36m-[m[32m1251[m[36m-[m                flash(
[35mapp.py[m[36m-[m[32m1252[m[36m-[m                    f"Invalid OTP. {remaining} attempts remaining.",
[35mapp.py[m[36m-[m[32m1253[m[36m-[m                    "error"
[35mapp.py[m[36m-[m[32m1254[m[36m-[m                )
[35mapp.py[m[36m-[m[32m1255[m[36m-[m            else:
[35mapp.py[m[36m-[m[32m1256[m[36m-[m                flash(
[35mapp.py[m[36m-[m[32m1257[m[36m-[m                    "Too many incorrect attempts. Please request a new OTP.",
[35mapp.py[m[36m-[m[32m1258[m[36m-[m                    "error"
[35mapp.py[m[36m-[m[32m1259[m[36m-[m                )
[35mapp.py[m[36m-[m[32m1260[m[36m-[m
[35mapp.py[m[36m-[m[32m1261[m[36m-[m            return redirect(url_for("verify_reset_otp"))
[35mapp.py[m[36m-[m[32m1262[m[36m-[m
[35mapp.py[m[36m-[m[32m1263[m[36m-[m        session["reset_verified"] = True
[35mapp.py[m[36m-[m[32m1264[m[36m-[m
[35mapp.py[m[36m-[m[32m1265[m[36m-[m        session.pop("reset_otp", None)
[35mapp.py[m[36m-[m[32m1266[m[36m-[m        session.pop("reset_otp_expires", None)
[35mapp.py[m[36m-[m[32m1267[m[36m-[m        session.pop("reset_otp_attempts", None)
[35mapp.py[m[36m-[m[32m1268[m[36m-[m
[35mapp.py[m[36m-[m[32m1269[m[36m-[m        return redirect(url_for("reset_password"))
[35mapp.py[m[36m-[m[32m1270[m[36m-[m
[35mapp.py[m[36m-[m[32m1271[m[36m-[m    return render_template("verify_reset_otp.html")
[35mapp.py[m[36m-[m[32m1272[m[36m-[m
[35mapp.py[m[36m-[m[32m1273[m[36m-[m
[35mapp.py[m[36m-[m[32m1274[m[36m-[m# ==========================================
[35mapp.py[m[36m-[m[32m1275[m[36m-[m# RESET PASSWORD
[35mapp.py[m[36m-[m[32m1276[m[36m-[m# ==========================================
[35mapp.py[m[36m-[m[32m1277[m[36m-[m
[35mapp.py[m[36m-[m[32m1278[m[36m-[m@app.route("/reset-password", methods=["GET", "POST"])
[35mapp.py[m[36m-[m[32m1279[m[36m-[mdef reset_password():
[35mapp.py[m[36m-[m[32m1280[m[36m-[m
[35mapp.py[m[36m-[m[32m1281[m[36m-[m    if not session.get("reset_admin_id"):
[35mapp.py[m[36m-[m[32m1282[m[36m-[m        return redirect(url_for("forgot_password"))
[35mapp.py[m[36m-[m[32m1283[m[36m-[m
[35mapp.py[m[36m-[m[32m1284[m[36m-[m    if not session.get("reset_verified"):
[35mapp.py[m[36m-[m[32m1285[m[36m-[m        return redirect(url_for("verify_reset_otp"))
[35mapp.py[m[36m-[m[32m1286[m[36m-[m
[35mapp.py[m[36m-[m[32m1287[m[36m-[m    if request.method == "POST":
[35mapp.py[m[36m-[m[32m1288[m[36m-[m
[35mapp.py[m[36m-[m[32m1289[m[36m-[m        new_password = request.form.get("new_password", "")
[35mapp.py[m[36m-[m[32m1290[m[36m-[m        confirm_password = request.form.get("confirm_password", "")
[35mapp.py[m[36m-[m[32m1291[m[36m-[m
[35mapp.py[m[36m-[m[32m1292[m[36m-[m        if not new_password or not confirm_password:
[35mapp.py[m[36m-[m[32m1293[m[36m-[m            flash(
[35mapp.py[m[36m-[m[32m1294[m[36m-[m                "Please fill in all password fields.",
[35mapp.py[m[36m-[m[32m1295[m[36m-[m                "error"
[35mapp.py[m[36m-[m[32m1296[m[36m-[m            )
