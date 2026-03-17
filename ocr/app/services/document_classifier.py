"""
document_classifier.py

Classification d'images de documents (facture / devis) avec Keras + EfficientNetB0.
Ce module est appelé EN PREMIER dans le pipeline, avant l'OCR.

Fonctions principales :
    build_model()       - construit le modèle EfficientNetB0 (transfer learning)
    train_model(...)    - entraîne depuis un dossier structuré train/ + val/
    load_classifier()   - charge un modèle sauvegardé (.keras)
    classify_image()    - prédit le type d'un document à partir d'une image NumPy

Structure attendue pour l'entraînement :
    data_dir/
        train/
            devis/     (images .png / .jpg)
            facture/   (images .png / .jpg)
        val/
            devis/
            facture/

Mapping des classes (ordre alphabétique Keras) :
    0 → devis
    1 → facture
"""

import os

import cv2
import numpy as np

IMG_SIZE = (224, 224)

# Classe 0 = devis, classe 1 = facture (ordre alphabétique imposé par Keras)
LABELS = {0: "devis", 1: "facture"}


# ---------------------------------------------------------------------------
# Prétraitement image → tenseur
# ---------------------------------------------------------------------------

def preprocess_for_classification(image: np.ndarray) -> np.ndarray:
    """
    Prépare l'image pour EfficientNetB0.

    - Convertit grayscale → RGB si nécessaire
    - Redimensionne à (224, 224)
    - Ajoute la dimension batch : (1, 224, 224, 3)

    Args:
        image : tableau NumPy (H, W) ou (H, W, 3) ou (H, W, 4)

    Returns:
        tenseur float32 de forme (1, 224, 224, 3)
    """
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    image = cv2.resize(image, IMG_SIZE)
    return np.expand_dims(image.astype(np.float32), axis=0)


# ---------------------------------------------------------------------------
# Construction du modèle
# ---------------------------------------------------------------------------

def build_model():
    """
    Construit un EfficientNetB0 avec tête de classification binaire.

    Architecture :
        EfficientNetB0 (ImageNet, couches gelées)
        → GlobalAveragePooling2D
        → Dropout(0.2)
        → Dense(1, sigmoid)   ← 0 = devis, 1 = facture

    Returns:
        keras.Model compilé
    """
    import tensorflow as tf

    keras = tf.keras
    layers = tf.keras.layers

    base_model = keras.applications.EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(224, 224, 3),
    )
    base_model.trainable = False

    inputs = keras.Input(shape=(224, 224, 3))
    x = keras.applications.efficientnet.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


# ---------------------------------------------------------------------------
# Entraînement
# ---------------------------------------------------------------------------

def train_model(
    data_dir: str,
    model_save_path: str = "model_classifier.keras",
    epochs: int = 15,
    batch_size: int = 16,
):
    """
    Entraîne le classifieur depuis un dossier structuré train/ + val/.

    Un EarlyStopping (patience=3) arrête l'entraînement si val_loss ne
    s'améliore plus. Le meilleur modèle est sauvegardé automatiquement.

    Args:
        data_dir        : chemin vers le dossier contenant train/ et val/
        model_save_path : fichier de sauvegarde du modèle (.keras)
        epochs          : nombre maximum d'epochs
        batch_size      : taille des batchs

    Returns:
        (model, history)
    """
    import tensorflow as tf

    keras = tf.keras

    train_ds = keras.utils.image_dataset_from_directory(
        os.path.join(data_dir, "train"),
        labels="inferred",
        label_mode="binary",
        image_size=IMG_SIZE,
        batch_size=batch_size,
        shuffle=True,
        seed=42,
    )
    val_ds = keras.utils.image_dataset_from_directory(
        os.path.join(data_dir, "val"),
        labels="inferred",
        label_mode="binary",
        image_size=IMG_SIZE,
        batch_size=batch_size,
        shuffle=False,
    )

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    model = build_model()
    model.summary()

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        ),
        keras.callbacks.ModelCheckpoint(
            model_save_path,
            monitor="val_loss",
            save_best_only=True,
        ),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
    )

    print(f"\nModèle sauvegardé : {model_save_path}")
    return model, history


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------

def load_classifier(model_path: str = "model_classifier.keras"):
    """
    Charge un modèle Keras depuis le disque.

    Args:
        model_path : chemin vers le fichier .keras

    Raises:
        FileNotFoundError : si le fichier n'existe pas

    Returns:
        keras.Model chargé
    """
    import tensorflow as tf

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Modèle introuvable : {model_path}\n"
            "Entraîne d'abord le modèle avec train_model() "
            "ou place le fichier model_classifier.keras dans le dossier services/."
        )
    return tf.keras.models.load_model(model_path)


# ---------------------------------------------------------------------------
# Inférence
# ---------------------------------------------------------------------------

def classify_image(image: np.ndarray, model) -> dict:
    """
    Classifie une image et retourne le type de document avec son score de confiance.

    Args:
        image : image NumPy (grayscale ou RGB), typiquement sortie de preprocess()
        model : modèle Keras chargé via load_classifier()

    Returns:
        {
            "document_type":             "facture" | "devis",
            "classification_confidence": float  (0.0 – 1.0)
        }
    """
    tensor = preprocess_for_classification(image)
    score = float(model.predict(tensor, verbose=0)[0][0])

    if score >= 0.5:
        return {
            "document_type": "facture",
            "classification_confidence": round(score, 4),
        }
    return {
        "document_type": "devis",
        "classification_confidence": round(1.0 - score, 4),
    }


# ---------------------------------------------------------------------------
# Point d'entrée CLI (entraînement)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Entraînement du classifieur Keras facture / devis"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Chemin vers le dossier data contenant train/ et val/",
    )
    parser.add_argument(
        "--output",
        default="model_classifier.keras",
        help="Chemin de sauvegarde du modèle (défaut : model_classifier.keras)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=15,
        help="Nombre d'epochs max (défaut : 15, EarlyStopping peut arrêter avant)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Taille des batchs (défaut : 16)",
    )
    args = parser.parse_args()

    train_model(
        data_dir=args.data,
        model_save_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
