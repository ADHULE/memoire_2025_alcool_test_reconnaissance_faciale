import cv2

def afficher_flux_camera(url_ou_indice):
    """
    Affiche le flux vidéo d'une caméra spécifiée par son URL ou son indice.

    Args:
        url_ou_indice (str ou int): L'URL du flux vidéo (pour une caméra IP)
                                     ou l'indice de la caméra locale (0 pour la caméra par défaut).
    """
    cap = cv2.VideoCapture(url_ou_indice)

    if not cap.isOpened():
        print(f"Erreur: Impossible d'ouvrir la caméra à l'adresse/l'indice : {url_ou_indice}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Flux vidéo terminé ou erreur de lecture.")
            break

        cv2.imshow("Flux Caméra", frame)

        # Quitter la boucle si la touche 'q' est pressée
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Remplacez ceci par l'adresse IP et le chemin de votre caméra IP (si elle utilise HTTP MJPEG)
    # Exemple pour une caméra IP MJPEG:
    camera_url = "http://192.168.10.10/video.mjpg"
    #
    # Si vous voulez utiliser la webcam locale (par défaut):
    camera_source = camera_url

    afficher_flux_camera(camera_source)

    # Si vous avez trouvé l'URL de votre caméra IP, utilisez-la à la place de camera_source:
    # afficher_flux_camera(camera_url)