#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <gflags/gflags.h>
#include <fstream>
#include <sstream>

#define BOOST_NO_CXX11_SCOPED_ENUMS
#include <boost/filesystem.hpp>
#undef BOOST_NO_CXX11_SCOPED_ENUMS

using namespace std;
using namespace cv;


#define INTER_LINEAR_EXACT 5
#define MAX_PATH_LEN 256
#define ACCESS(fileName,accessMode) access(fileName,accessMode)
#define MKDIR(path) mkdir(path,S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH)

DEFINE_int32(draw_original, 0, "the number of similarity images");
DEFINE_string(img_path, "", "the folder that contain images");

// std::string img_path = "./data/imgorg";
// std::string command = "python ./python/cpp_use.py";
// std::string high_simipath = "./data/img_simi/";


bool CreateDirectory(const string &directoryPath);
string ImageHashValue(IplImage* src);
void ImageSimilarity(string &str1,string &str2,vector<double>&my_res);
void Vec2txt(vector<double> &for_draw_, std::string draw_path);
// bool IsFileExistent(const boost::filesystem::path& path);
inline bool IsFileExist(const std::string& name);



int main(int argc, char** argv)
{
    ::google::ParseCommandLineFlags(&argc, &argv, true);
#ifndef GFLAGS_GFLAGS_H
    namespace gflags = google;
#endif

    gflags::ParseCommandLineFlags(&argc, &argv, true);
    int simi_nub = 0;
    int draw_original = FLAGS_draw_original;
    std::string img_path = FLAGS_img_path;
    int index = img_path.find_last_of("/\\");
    std::string filename = img_path.substr(index+1);
    // cout << "filename: " << filename << endl;
    std::string draw_path = "./data/result/" + filename + "/" + filename + "_simi.txt";
    // cout << "test============: " << draw_path << endl;
    std::string command = "python ./python/cpp_use.py " + draw_path;
    std::string high_simipath = "./data/img_simi/" + filename + "/";
    if (CreateDirectory(high_simipath)){
        cout << "now build folder for saving high similarity images" << endl;
    }
    
    std::vector<cv::String> img;
    cv::glob(img_path, img, false);
    size_t count = img.size();
    vector<double> for_draw;

    for (size_t i = 0; i < (count-1); i++)
    {
        // cout << img[i] << endl;
        Mat image1_cv = imread(img[i]);
        Mat image2_cv = imread(img[i+1]);
        IplImage temp1 = (IplImage)image1_cv;
        IplImage* image1 = &temp1;
        IplImage temp2 = (IplImage)image2_cv;
        IplImage* image2 = &temp2;
        // IplImage* image1 = cvLoadImage("../image/2.jpg",1);
        // IplImage* image2 = cvLoadImage("../image/3.jpg",1);
        // cvShowImage("image1",image1);
        // cvShowImage("image2",image2);
        string imgPrint1 = ImageHashValue(image1);
        string imgPrint2 = ImageHashValue(image2);
        // cout << "img1: " << imgPrint1 << "img2: " << imgPrint2 << endl;

        // my std
        double similarity_ = 1.0;
        double Hamming_Distance_ = 0.0;
        vector<double> my_res;
        my_res.push_back(similarity_);
        my_res.push_back(Hamming_Distance_);
        ImageSimilarity(imgPrint1,imgPrint2,my_res);
        double similarity = my_res[0];
        double Hamming_Distance = my_res[1];
        // cout << "Hamming distance of two images is " << Hamming_Distance << endl;
        cout<<"The similarity of two images is "<<similarity*100<<"%"<<endl;
        if(similarity>=0.9){
            cout<<"The two images are extremely similar."<<endl;
            int index_img_name = img[i].find_last_of("/");
            std::string img_name = img[i].substr(index_img_name + 1);
            // std::cout << "name: " << img_name << std::endl;
            std::string High_simi = "mv " + img[i] + " " + high_simipath + img_name;
            // std::cout << "test: " << High_simi << std::endl;
            std::cout << "================similarity>90================" << std::endl;
            system(High_simi.c_str());
            simi_nub++;
        }
        else if(similarity>=0.8&&similarity<0.9)
            cout<<"The two images are pretty similar."<<endl;
        else if(similarity>=0.7&&similarity<0.8)
            cout<<"The two images are a little similar."<<endl;
        else if(similarity<0.7)
            cout<<"The two image are not similar."<<endl;
            cout<<endl;

        for_draw.push_back(similarity);
        // cvWaitKey(0);
        // cvDestroyAllWindows();
    }
    if (draw_original == 0){
        std::string draw_path = "./data/result/" + filename + "/" + filename + "_simi_original.txt";
        if(!IsFileExist(draw_path)){
            std::string command = "python ./python/cpp_use.py " + draw_path;
            Vec2txt(for_draw, draw_path);
            system(command.c_str());
        }
    }
    if (simi_nub)
    {
        std::cout << "the number of similar images is greater than 0, now restart filter" << std::endl;
        std::string commond_simi = "./build/img_filter --img_path " + img_path + " --draw_original 1";
        system(commond_simi.c_str());
    }
    else if (!simi_nub)
    {
        Vec2txt(for_draw, draw_path);
        system(command.c_str());
    }
    return 0;
}

bool CreateDirectory(const string &directoryPath) {
    int dirPathLen = directoryPath.length();
    if (dirPathLen > MAX_PATH_LEN) {
        return false;
    }

    char tmpDirPath[MAX_PATH_LEN] = { 0 };
    for (int i = 0; i < dirPathLen; ++i) {
        tmpDirPath[i] = directoryPath[i];
        if (tmpDirPath[i] == '\\' || tmpDirPath[i] == '/') {
            if (ACCESS(tmpDirPath, 0) != 0) {
                if (MKDIR(tmpDirPath) < 0) {
                    return false;
                }
            }
        }
    }
    return true;
}

void Vec2txt(vector<double> &for_draw_, std::string draw_path)
{
    ofstream outfile(draw_path.c_str());
    for(auto &r:for_draw_)
    {
        outfile << r << endl;
    }
}

string ImageHashValue(IplImage* src)
{
    string resStr(64,'\0');
    IplImage* image = cvCreateImage(cvGetSize(src),src->depth,1);
    if(src->nChannels == 3)
        cvCvtColor(src,image,CV_BGR2GRAY);
    else
        cvCopy(src,image);
    IplImage* temp = cvCreateImage(cvSize(8,8),image->depth,1);
    cvResize(image,temp);
    // cvShowImage("resize_GRAY",image);
    uchar* pData;
    // for(int i=0; i<temp->height; i++)
    // {
    //     pData =(uchar* )(temp->imageData+i*temp->widthStep);
    //     for(int j=0; j<temp->width;j++)
    //         pData[j]= pData[j]/4;
    // }
    int average = cvAvg(temp).val[0];
    int index = 0;
    for(int i=0; i<temp->height; i++)
    {
        pData =(uchar* )(temp->imageData+i*temp->widthStep);
        for(int j=0; j<temp->width;j++)
        {
            if(pData[j]>=average)
                resStr[index++]='1';
            else
                resStr[index++]='0';
        }
    }
    return resStr;
}


void ImageSimilarity(string &str1,string &str2,vector<double> &my_res)
{
    double similarity = 1.0;
    double Hamming_Distance = 0.0;
    for(int i=0;i<64;i++)
    {
        char c1 = str1[i];
        char c2 = str2[i];
        if(c1!=c2)
        {
            similarity = similarity -1.0/64;
            Hamming_Distance += 1;
        }
    }
    my_res[0] = similarity;
    my_res[1] = Hamming_Distance;
    // return similarity;
}


// bool IsFileExistent(const boost::filesystem::path& path) {

//     boost::system::error_code error;
//     auto file_status = boost::filesystem::status(path, error);
//     if (error) {
//         return false;
//     }

//     if (! boost::filesystem::exists(file_status)) {
//         return false;
//     }

//     if (boost::filesystem::is_directory(file_status)) {
//         return false;
//     }

//     return true;
// }

inline bool IsFileExist (const std::string& name) {
  struct stat buffer;   
  return (stat (name.c_str(), &buffer) == 0); 
}