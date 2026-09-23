# Vision-Mouse

Kamera üzerinden el hareketlerini izleyerek bilgisayar faresini fiziksel bir temasa gerek kalmadan kontrol etmenizi sağlayan, bilgisayarlı görü (computer vision) tabanlı sanal fare projesidir.

## 🚀 Özellikler

* **İmleç Kontrolü:** Fare imlecini hareket ettirmek için işaret parmağınızı kullanabilirsiniz. Sistem, parmak ucunuzun konumunu gerçek zamanlı olarak takip eder ve ekran koordinatlarına oranlar.
* **Tıklama İşlevi:** Başparmak ve işaret parmağınızı birbirine dokundurduğunuzda (çimdik/pinch hareketi) farenin sol tıklama (click) işlemi algılanır ve işletim sistemine iletilir.
* **Düşük Gecikme:** Optimize edilmiş el iskeleti algılama modeli sayesinde gerçek zamanlı ve akıcı bir deneyim sunar.

## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

* **Python:** Projenin ana geliştirme dili.
* **OpenCV (`cv2`):** Web kamerasından video akışını yakalamak, kareleri okumak ve görüntüyü işlemek (renk uzayı dönüşümleri, ekrana çizim yapma) için kullanıldı.
* **MediaPipe:** Google tarafından geliştirilen bu framework, görüntü üzerindeki eli tespit edip 21 farklı eklem noktasının (hand landmarks) koordinatlarını yüksek hassasiyetle çıkarmak için kullanıldı.
* **PyAutoGUI:** MediaPipe'tan alınan parmak koordinatlarını bilgisayar ekranının çözünürlüğüne dönüştürerek donanımsal fare hareketlerini ve tıklama olaylarını simüle etmek için entegre edildi.


