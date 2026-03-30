# a-small-Aspect-Ratio-Bucketing-and-multires-tool
!Warning!: make a copy of your original dataset. This is vibe coded slop. I provided the vibe, Claude the slop. And sometimes vice versa. Shows resolutions after aspect ratio bucketing, uses padding to push into different buckets. Can be used for datasets for Onetrainer https://github.com/Nerogar/OneTrainer

Background: After discovering the debug mode I found out three things. First, what some of my training settings actually do behind the scenes, namely having multiple resolution in the resolution field in the training tab and aspect ratio bucketing on: Having multiple resolutions scales each image randomly to one of the resolutions you put in the field, which can be chaotic - and aspect ratio bucketing influences how they get scaled and in which bucket they land. Second: That debug mode is a great tool to see on which images a LoRa or model actually get trained. Third: How royally the VAE can f up your images when decoding takes place (thanks, SDXL).
Can't change much about the VAE, but can try to do something about aspect ratio bucketing or at least see what it will do to a dataset.

## Aspect ratio bucketing
Quick reminder what this nice little technique does:
- allows you to have different aspect ratio images in your dataset
- no weird cropping everything to one size by OT
Overall, very nice to have.
How does it achieve this?
It goes through a small list oft 17 possible aspect ratios like 1:1, 4:1, 1.75:1 (16/9 approx) and their counterparts and decides in which bucket your input images go depending on their width and height. Then it makes sure the images fit the bucket using your chosen training resolution and a factor depending on your model.
You set your training resolution to 1024? Both your 4k high fidelity raw picture of your cat and the 64x64 icon sized reminder of your mom will be scaled to fit that training resolution.
Example: You have a 2:3 - 600 x 900 (540000 pixels) image.
Aspect ratio bucketing will
1. Determine AR = 1.5
2. see this is an exact match for possible aspect ratios, but not yet for our training resolution.
3.  scale each side of the image to the training resolution, for example the height: 900   ÷   √ ( 900   ×   600 )   ×   1024  = 1.254,13
4. see that this is not a fitting integer for our model (for example SDXL), so the values get quantized with the model-specific factor (in this case 64) and rounded:  round(1254,13 / 64) * 64 = 20 * 64 = 1280
5. in the end scale the 600 x 900 (540.000 pixels) image to 832 x 1280 (1.064.960 pixels)

So what can the tool do for you here? Probably not much, but more than nothing.

<img width="3833" height="884" alt="image" src="https://github.com/user-attachments/assets/439d825b-e500-4a2f-8e80-03ef3a26be43" />


## See what your images will scale to & recommended training resolution

- load a folder and scan, to see what each image will scale to at any given training resolution with aspect ratio bucketing on. This basically just tells you what aspect ratio bucketing will do, in case you want to know beforehand
- you can change the quantization, so if you know how your model quantizes, you will see how the calculations and output resolution changes (just in case you wondered why your puny 600x900 scales all the way up to 1280 like I did)

recommended training resolution:
this is not a recommendation based on quality or your model, but purely on size of the input image. Don't think your 64x64 should be trained at 1024? use the recommended training resolution. calculated with a minimum, a maximum and steps, it looks for the smallest training resolution that is larger than your image. Example: 1080x1080 picture with min set to 512, max to 2048, steps to 128 would get recommended a training resolution of 1152. set steps to 256, recommendation would be 1280.
Can do individually per image or for all at the same time. Click 'sort to T folders' and the tool will create subfolders named with the training solution, put all the images there accordingly, along with any .txts that have the same name (so you don't have to manually sort through the caption files in case you created them beforehand).
Could possibly be used to create different size buckets, or for multires training based on concepts. Probably the most useful part of the tool.

## Fit within training resolution
Toggle at the top left.
While training resolution determines aspect ratio buckets, due to quantization the rescaled images from aspect ratio bucketing can still be larger than the training resolution. So the tool tells you not only to what resolution the image will scale, but if even one side is larger than the training resolution. This is stricter and mathematically incorrect (for 1024 training resolution, 1152x896 images would get marked just because one side is larger than 1024, even though 1152x896 is smaller than 1024x1024), but I really wanted to make sure my smaller images don't get scaled to huge proportions.
Pad:
This is where the 'pad' function comes in. Instead of cropping, we pad the sides just to make sure all sides stay under the training resolution value after aspect ratio bucketing is done with them. In practice, pixels are added to the canvas, and in the end, everything will be square after aspect ratio bucketing. Meaning it should all land in the same bucket, but without cropping.
Debatable usefulness. Might be nice/work with masked training or if you don't care about black borders. I mostly use images with the background removed, so it is not an issue for me. Impact on quality of LoRa: unknown. But at least the images that get trained on will be less pixelated from scaling.
Scale + Pad:
Similar, but instead of just adding pixels, we scale the original image down before padding pixels. Even less pixelation from scaling. But also loss of detail.

## Minimal bucket
The other side of the toggle at the top left.
Motto: Don't be a square! (squares still allowed, though).
Instead of padding so everything ends up a square and the sides smaller than the training resolution value, we accept that the sides can be larger. We still try to minimize huge upscaling for small pictures, by pushing images into other aspect ratio buckets by padding them.
Our 600x900 (540.000) image at 1024 training resolution does not end up a 832x1280 (1.064.960) BEHEMOTH anymore, but only gets scaled to a 896x1152 (1.032.192) bEHEMOTh, all for the price of adding 38px width (thats only 19 per side!).

For images larger than the training resolution, we take the opposite approach, looking for the largest bucket (pixelwise) that we can get. This way, our 1265x910 (1.151.150) !BEHEMOTH! does not turn into a 1152x896 (1.032.192) bEHEMOTh, but stays at least a 1280x832 (1.064.960) BEHEMOTH, just by adding 10 px width.

Buckets qualifying here were tried to keep somewhat sane, given how questionable the tool otherwise is. They only can be neighbouring buckets.  An image belonging to the 1.75 ratio bucket would only be padded to land in the 1.5 or 2 bucket, even if the 2.5 bucket might look juicy given its small pixel size.

Usefulness: Could be somewhat more useful, depending on dataset and other settings, and if checking how much pixels get added.


# installation and usage
- download
- install.bat
- run.bat
- browser opens, add folder play around
