import os
import zipfile

if __name__ == '__main__':
    fileNames = os.listdir("C:/Users/alaa2/OneDrive/Desktop/point_to_point/generated_trees/")

    i = 0
    for filename in fileNames:
        zip = zipfile.ZipFile(
            "C:/Users/alaa2/OneDrive/Desktop/point_to_point/generated_trees_zip/{}.zip".format(filename), "w",
            zipfile.ZIP_DEFLATED)
        zip.write("C:/Users/alaa2/OneDrive/Desktop/point_to_point/generated_trees/{}".format(filename))
        zip.close()
        print("Done {}".format(i))
        i = i + 1
