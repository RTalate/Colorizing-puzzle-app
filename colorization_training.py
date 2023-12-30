# -*- coding: utf-8 -*-

# imports

#%%
import torch #requirement: pip install pytorch. Version depends on your build, if unsure, just install pytorch and it will run on the cpu instead of the gpu. 
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os
import splitfolders #requirement: pip install split-folders==0.5.1
#%%


# Define the colorization model
class ColorizationNet(nn.Module):
    def __init__(self):
        super(ColorizationNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=5, stride=1, padding=4,
                               dilation=2)  # grayscale to 64 feature maps
        self.conv2 = nn.Conv2d(64, 64, kernel_size=5, stride=1, padding=4, dilation=2)  # 64 to 64
        self.conv3 = nn.Conv2d(64, 128, kernel_size=5, stride=1, padding=4,
                               dilation=2)  # increase of feature maps to capture more complex patterns
        self.conv4 = nn.Conv2d(128, 3, kernel_size=5, stride=1, padding=4, dilation=2)  # 3 channels: RGB

    def forward(self, x):
        x = nn.functional.relu(self.conv1(x))
        x = nn.functional.relu(self.conv2(x))
        x = nn.functional.relu(self.conv3(x))
        x = torch.sigmoid(self.conv4(x))

        return x


if __name__ == "__main__":
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#%% Load the dataset, split it into train and test. Fix the seed to have the same split for everybody.
    img_path=r"C:\Users\rayan\Documents\GitHub\Projet infra\images folder\color"
    # img_path = r"C:\Users\Thomas\Downloads\Colorisation-d-images-via-le-machine-learning-dev_scraping\images folder\color_planes"
    inp=img_path
    output=r"C:\Users\rayan\Documents\GitHub\Projet infra\images folder\split"
    
    splitfolders.ratio(inp, output=output, seed=123, ratio=(.85, 0,0.15)) 
    


# %%

    # cette ligne indique la façon dont on transforme les images pour le dataset d'entraînement. On en profite pour effectuer de la data augmentation.
    train_transform = transforms.Compose([
        transforms.TrivialAugmentWide(num_magnitude_bins=31),
        transforms.ToTensor()  # normalise les valeurs des pixels.
    ])
    # TrivialAugment est une méthode de Data Augmentation: on choisit une méthode d'augmentation parmi une sélection de méthodes triviales (baisse de luminosité, retournement de l'image, etc.), plus ou moins impactantes, et appliquées à un degré plus ou moins intense. num_magnitude bins, situé entre 1 et 31, augmente la probabilité d'avoir une transformation plus sérieuse et appliquée de façon plus intense.

    test_transform = transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    train_dataset = datasets.ImageFolder(root=output+"\\train", transform=train_transform)
    test_dataset = datasets.ImageFolder(root=output+"\\test", transform=test_transform)
    # attention: pour le chemin menant aux images, ImageFolder attend un dossier comportant des sous-dossiers, un pour chaque classe. Pour cet exercice, il n'est pas question de classifier les images, il n'y aura donc qu'un seul sous-dossier
    # %%
   
    train_loader = DataLoader(dataset=train_dataset, batch_size=1, num_workers=os.cpu_count(), shuffle=True)
    # num_workers=os.cpu_count() pour que le DataLoader puisse utiliser un maximum de processeurs pour charger les données.

    test_loader = DataLoader(dataset=test_dataset, batch_size=1, num_workers=os.cpu_count(), shuffle=True)

    transform = transforms.Compose([
        transforms.ToTensor(),
    ])


    model = ColorizationNet().to(device)

    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)


    # Convert RGB image to grayscale
    def rgb_to_gray(img):
        return img.mean(dim=1, keepdim=True)


    # Training loop
    EPOCHS = 15
    for epoch in range(EPOCHS):
        for i, (images, _) in enumerate(train_loader):
            grayscale_images = rgb_to_gray(images).to(device)
            images = images.to(device)

            # Forward pass
            outputs = model(grayscale_images)
            loss = criterion(outputs, images)

            # Backward pass and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Print statistics
            if i % 100 == 0:
                print(f"Epoch [{epoch + 1}/{EPOCHS}], Step [{i + 1}/{len(train_loader)}], Loss: {loss.item():.4f}")

    print("Finished Training")

    # save model parameters

    # path of the file
    # à changer + tard : remplacer par le chemin du projet pour avoir le fichier à disposition
    chemin_fichier_params = 'modele_1.pth' # avec cette syntaxe, le fichier est créé là où on se situe

    # save parameters in this file
    torch.save(model.state_dict(), chemin_fichier_params)

    print("Parameters saved")


