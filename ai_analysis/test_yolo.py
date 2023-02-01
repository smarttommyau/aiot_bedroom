import torch

model = torch.hub.load('ultralytics/yolov5', 'yolov5x6', pretrained=True)
model.classes = [0,67]
img = "test0.png"
torch.set_num_interop_threads(8)
torch.set_num_threads(8)
result = model(img)

result.pandas()
