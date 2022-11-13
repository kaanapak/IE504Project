# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random

import pandas as pd
import math

class Patient:


    def __init__(self,no,sp,x,y,distances,patient_count):
        self.no=no
        self.sp = sp
        self.np = self.calculate_np()
        self.x = x
        self.y = y
        self.distances=distances
        self.patient_count=patient_count
        self.is_assigned=False
        self.temp_lostcost=0
        self.temp_lostPoint=0
        self.temp_distancePoint=0;

    def calculate_np(self,planing_horizon = 14):
        long_alpha = 3
        short_alpha = 2
        return (planing_horizon - (long_alpha - self.sp)) / short_alpha

    def distance_to_Patient(self,patient):
        return self.distances.iloc[patient.no]

    def distance_to_Center(self,center):
        return self.distances.iloc[self.patient_count+center.Instance_no]

    #def getTempDistancePoint(self,network,center):
        #return network.distancePointCalculator(self, center)
    def getTempDist(self):
        return self.temp_distancePoint


class Center:
    def __init__(self,no,Instance_no,name,district,x,y,number_of_machines,distances,patient_count):
            self.name=name
            self.no=no
            self.Instance_no=Instance_no
            self.district=district
            self.x = x
            self.y = y
            self.number_of_machines = number_of_machines
            self.capacity = self.calculate_capacity()
            self.distances = distances
            self.patient_count = patient_count
            self.patient_In_Center=0
            self.is_Full=False
            self.remaining_capacity=self.capacity
            self.patients=[]


    def addPatient(self,patient):
        patient.is_assigned=True
        self.patients.append(patient)
        self.remaining_capacity-=1
        self.patient_In_Center+=1
        if(self.remaining_capacity==0):
            self.is_Full=True

    def distance_to_Patient(self,patient):
        return self.distances.iloc[int(patient.no)]

    def distance_to_Center(self,center):
        return self.distances.iloc[self.patient_count+int(center.Instance_no)]

    def calculate_capacity(self,planing_horizon = 14,L = 4):
        long_alpha = 3
        short_alpha = 2

        c = 1
        inequality_lhs = long_alpha * c + 1
        inequality_rhs_top = (planing_horizon - (long_alpha - 1)) * c
        inequality_rhs_bottom = (planing_horizon - (long_alpha - 1) - L * short_alpha)/long_alpha + L * 0.5
        inequality_rhs = inequality_rhs_top / inequality_rhs_bottom

        while not inequality_lhs <= inequality_rhs and c < 100:
            c += 1
            inequality_lhs = long_alpha * c + 1
            inequality_rhs_top = (planing_horizon - (long_alpha - 1)) * c
            inequality_rhs_bottom = ((planing_horizon - (long_alpha - 1) - L * short_alpha) / long_alpha) + (L * 0.5)
            inequality_rhs = inequality_rhs_top / inequality_rhs_bottom

        capacity_at_day_0 = self.number_of_machines * (8 / 4)  #8 hours on a day assumed
        #capacity_at_day_* (Ch0) = num_of_machines * hours_in_a_day / length of a long session (4-hours)

        #capacity = (long_alpha * self.number_of_machines + 1) * math.floor(capacity_at_day_0 / c) + long_alpha * (capacity_at_day_0 % c)
        #print(capacity)

        capacity = self.number_of_machines * 3.5
        return capacity


class Network:
    def __init__(self,simulation_scope,total_patients):
        self.centers=[]
        self.patients=[]
        self.simulation_scope = simulation_scope

        self.center_count=0
        self.total_patients=total_patients
        self.patient_count=0
        self.assigned_patients=0

    def Print(self):
        total_patient=0;
        total_distance = 0
        for center in self.centers:
            total_patient+=center.patient_In_Center
            print("Center ",center.no," Name ",center.name," Number of Patients ",center.patient_In_Center)
            current_patient_list=center.patients
            sp1Patient=0
            sp2Patient=0
            sp3Patient=0
            current_distance=0
            for patient in current_patient_list:
                if(patient.sp==1):
                    sp1Patient+=1
                if(patient.sp==2):
                    sp2Patient+=1
                if(patient.sp==3):
                    sp3Patient+=1

                current_distance+=patient.distance_to_Center(center)
            print("Number of sp1: ",sp1Patient," Number of sp2 ",sp2Patient, "Number of sp3 ",sp3Patient)
            print("Total Distance at center ",current_distance)
            print("------------")
            total_distance+=current_distance

        print('*******')
        print('Total customers served ',total_patient)
        print('Number of transferred out ',(self.patient_count-total_patient))
        print('Total distance ',total_distance)




    def add_patient(self,patient):
        self.patients.append(patient)
        self.patient_count+=1

    def add_center(self,center):
        self.centers.append(center)
        self.center_count+=1

    def candidate_patients(self,center,coverage):
        patient_list=[]
        for patient in self.patients:
            if (patient.is_assigned == False) and (center.distance_to_Patient(patient) <= coverage):
                patient_list.append(patient)

        return patient_list

    def nearest_otherC(self, patient,Rcenter):
        min_distance = 10000
        min_center=0
        for center in self.centers:
            if ((center.is_Full == False) and (center.Instance_no == Rcenter.Instance_no)):
                if (patient.distance_to_Center(center) < min_distance):
                    min_distance = patient.distance_to_Center(center)
                    min_center = center
        return min_distance, min_center

    def nearest_center(self,patient):
        min_distance = 10000
        for center in self.centers:
            if (center.is_Full == False):
                if (patient.distance_to_Center(center) < min_distance):
                    min_distance = patient.distance_to_Center(center)
                    min_center = center
        return min_distance, min_center

    def lostCostCalculator(self, patient,center):
        patient.temp_lostcost = self.nearest_otherC(patient,center)[0] - patient.distance_to_Center(center)

    def lostPointCalculator(self, patient,center):
        self.lostCostCalculator(patient,center)
        patient.temp_lostPoint = patient.temp_lostcost * patient.np

    def distancePointCalculator(self, patient,center):
        if(patient.distance_to_Center(center)!=0):
         patient.temp_distancePoint = patient.np / patient.distance_to_Center(center)
        else:
            patient.temp_distancePoint =0

    def lostPointList(self, center, coverage):
        patient_list = self.candidate_patients(center,coverage)
        for patient in patient_list:
            self.lostPointCalculator(patient,center)
        return  sorted(patient_list, key=lambda x: x.temp_lostPoint, reverse=True)

    def distPointList(self, center, coverage):
        patient_list = self.candidate_patients(center,coverage)
        for patient in patient_list:
            self.distancePointCalculator(patient,center)
        #return sorted(patient_list, key=patient.temp_distancePoint,reverse=True)
        #return sorted(patient_list, key=Patient.getTempDist(Patient), reverse=True)
        return  sorted(patient_list, key=lambda x: x.temp_distancePoint, reverse=True)




    def assignbyLostPoint(self):
        for center in self.centers:
            patient_list=self.lostPointList(center,6)
            range_s=min(int(center.capacity),len(patient_list)-1)
            for i in range(0,range_s):
                center.addPatient(patient_list[i])
                self.assigned_patients += 1


    def assignbyDistPoint(self):
        for center in self.centers:
            patient_list = self.distPointList(center, 6)
            range_s = min(int(center.capacity), len(patient_list))
            for i in range(0, range_s):
                center.addPatient(patient_list[i])
                self.assigned_patients+=1




if __name__ == '__main__':
    dialysis_centers = pd.read_csv(r"dialysis_centers.csv",sep = ';')
    patient_coordinates=pd.read_csv(r"Koordinatlar.csv",sep = ';')
    patient_count=patient_coordinates.shape[0]
    distanceMatrix = pd.read_csv(r"UzaklıkMatris.csv", sep=';')
    network = Network(14,patient_count)
    #current_row=distanceMatrix.iloc[0]
    for index, row in patient_coordinates.iterrows():
        current_patient=Patient(row['Hasta No'],row['Sp'], row['Koordinat x'], row['Koordinat y'],distanceMatrix.iloc[int(row['Hasta No'])],patient_count)
        network.add_patient(current_patient)

    facility_instance=patient_coordinates.drop_duplicates(['Merkez/Hastane No'])
    facility_instance['Is_Instance']='Yes'
    #print(facility_instance)
    dialysis_centers = dialysis_centers.merge(facility_instance, how="left",on=['Merkez/Hastane No'])
    dialysis_centers=dialysis_centers[dialysis_centers['Is_Instance']=='Yes']


    center_instance_no=0
    distance_centers=distanceMatrix.tail(distanceMatrix.shape[0] -patient_count)

    for index, row in dialysis_centers.iterrows():

        current_center = Center(row['Merkez/Hastane No'],center_instance_no,row['Diyaliz merkezi'],row['İlçe'], row['Koordinat x_x'], row['Koordinat y_x'],  row['Makineler'],distance_centers.iloc[center_instance_no],patient_count)
        center_instance_no+=1
        network.add_center(current_center)

    network.assignbyLostPoint()
    #network.assignbyDistPoint()

    network.Print()