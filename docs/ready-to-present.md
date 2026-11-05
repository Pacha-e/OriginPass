# Ready to present: OriginPass demonstration

Status: 5 November 2026. The demonstration runs on the AWS EC2 deployment at `https://13-220-96-49.sslip.io`. The local server is the fallback. Check this page before the class.

## 1. Thirty minutes before the class

1. Start the AWS Academy Learner Lab and the instance `originpass-d4`. Note the public IPv4 address.
2. If the address is not `13.220.96.49`, the public name, the certificate and the settings change too. Do not improvise on the day: use the local fallback in section 4 and fix the deployment afterwards (`deploy/aws/README-AWS.md`).
3. Open `https://13-220-96-49.sslip.io/healthz/`. Expect a padlock and `{"status": "ok"}`.
4. Open the verification page of "Bolso textil demostrativo" (code from the printed sheet, under `https://13-220-96-49.sslip.io/v/<code>/`). Expect its photo to load; the nginx `/media/` route serves it.
5. Print `hoja-qr-1.png` from `04-Datos\entrega-4-qr\qr-https-definitivo` at 100% on US Letter paper. Check the logo on each code and the status text on the revoked passport.
6. Scan one printed code with a phone. It must open the HTTPS verification page.

## 2. Demonstration accounts

Use these accounts, all with the shared demonstration password. The password is defined in the seed command, `companies/management/commands/seed_demo.py`; it is not written in this document.

- contacto@labonga.co
- taller@tuchin.co
- comprador@correo.co
- contacto@textilesmedellin.example
- taller@cesteriausiacuri.example

The administrator account is not part of the demonstration.

## 3. Walkthrough (about ten minutes)

1. **Verify a passport.** Scan a printed code. Show the company, the verification track and the custody chain of "Sombrero vueltiao 21 vueltas": made by `taller@tuchin.co`, delivered to `contacto@labonga.co` in Montería, sold to `comprador@correo.co` in Cartagena.
2. **A revoked passport.** Open "Hamaca de San Jacinto": the page shows it as revoked and gives the reason.
3. **Receive a product.** On the claim page, read the passport QR with the phone camera, or upload a photo of it. The passport code fills in. The transfer code is the one the seller gives at the sale.
4. **Change password.** From the navigation bar, "Change password" (sign in first).
5. **Owner view.** Sign in as `taller@tuchin.co` to show the products and the open offer on "Sombrero vueltiao 15 vueltas".

## 4. Fallbacks

- **Camera denied or not available:** choose "Choose a photo" and upload a photo of the QR, or type the passport code.
- **Photo not read:** take a closer, sharper photo of the printed code, or type the code printed under it.
- **Site not answering:** start the instance first. If it still does not answer, continue on the laptop with `python manage.py runserver` and open the verification pages at `http://127.0.0.1:8000/v/<code>/`, typing the code from the printed sheet. The printed codes point to the HTTPS address, so they do not open the local server by scanning.
- **Duplicate-scan alert:** it appears in the administrator's alerts. It comes from the demonstration data, not from a real copy.

## 5. After the class

- Stop or terminate the instance so the Learner Lab budget is not used. Terminating deletes the database and the media files on the instance disk.
- Record in `docs/d4/seguimiento.md` what happened during the demonstration.

## Reference

- Update the server: `sudo bash /opt/originpass/app/deploy/aws/actualizar-ec2.sh 13-220-96-49.sslip.io`
- Deployment guide: `deploy/aws/README-AWS.md`