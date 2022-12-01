# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
import time
from collections import defaultdict

import pandas as pd
import math
from random import randrange
import copy

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
        self.temp_distancePoint=0
        self.temp_center=0

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
    def __init__(self,no,Instance_no,name,district,x,y,number_of_machines,distances,patient_count,ch0):
            self.name=name
            self.no=no
            self.Instance_no=Instance_no
            self.district=district
            self.x = x
            self.y = y
            self.number_of_machines = number_of_machines
            self.ch0 = ch0
            self.capacity = self.calculate_capacity()
            self.distances = distances
            self.patient_count = patient_count
            self.patient_In_Center=0

            if self.capacity > 0:
                self.is_Full = False
            else:
                self.is_Full = True
            self.remaining_capacity=self.capacity
            self.patients=[]

    def addPatient(self,patient):
        patient.is_assigned=True
        self.patients.append(patient)
        self.remaining_capacity-=1
        self.patient_In_Center+=1
        if(self.remaining_capacity<1):
            self.is_Full=True

    def remove_patient(self,patient):
        patient.is_assigned =False
        self.patients.remove(patient)
        self.remaining_capacity += 1
        self.patient_In_Center -=1
        self.is_Full = False

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

        #capacity_at_day_0 = self.number_of_machines * 0.2 * (8 / 4)  #8 hours on a day assumed
        #capacity_at_day_* (Ch0) = num_of_machines * hours_in_a_day / length of a long session (4-hours)
        ch0 = self.ch0

        capacity = (long_alpha * c + 1) * math.floor(ch0 / c) + long_alpha * (ch0 % c)
        print(capacity)

        #capacity = self.number_of_machines * 3.5
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
        self.total_capacity = 0



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

                current_distance += patient.distance_to_Center(center) * patient.np
            print("Number of sp1: ",sp1Patient," Number of sp2 ",sp2Patient, "Number of sp3 ",sp3Patient)
            print("Total Distance at center ",current_distance)
            print("------------")
            total_distance+=current_distance

        print('*******')
        print('Total customers served ',total_patient)
        print('Number of transferred out ',(self.patient_count-total_patient))
        print('Total distance ',total_distance)

    def objective_function(self):  # SEFA: UPDATE WITH VALUES OF BETA and SENDING A PATIENT OUTSIDE
        total_distance = 0
        #beta = 10
        epsilon = 0.001
        cost_of_sending_out = 200
        for center in self.centers:
            for patient in center.patients:
                total_distance += patient.distance_to_Center(center)*patient.np

        return total_distance

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
            patient.temp_distancePoint = 1 / (patient.distance_to_Center(center))
            #patient.temp_distancePoint = 1 / (patient.distance_to_Center(center) * patient.np)

        else:
            patient.temp_distancePoint = 0

    def distancePointCalculatorPatient(self,patient):

        min_distance, min_center = self.nearest_center(patient)
        #patient.temp_distancePoint = 1 / min_distance

        patient.temp_distancePoint = 1 / (min_distance * patient.np)

        patient.temp_center = min_center

    def patientListSorted(self):
        for patient in self.patients:
            self.distancePointCalculatorPatient(patient)
        return sorted(self.patients, key=lambda x: x.temp_distancePoint, reverse=True)

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
        return sorted(patient_list, key=lambda x: x.temp_distancePoint, reverse=True)

    def assign_patients_balanced_sp(self): #C2
        for center in self.centers:

            patient_list = self.distPointList(center, 25) #sorted by: patient.np / patient.distance_to_Center(center)
            remaining_sorted_patients = patient_list.copy()
            for i in range(round(center.capacity)//1):
                if center.is_Full:
                    break
                for sp in range(1,4):
                    if center.is_Full:
                        break
                    for patient in remaining_sorted_patients:
                        if center.is_Full:
                            break
                        if patient.sp == sp :
                            remaining_sorted_patients.remove(patient)
                            center.addPatient(patient)
                            self.assigned_patients += 1
                            break

    def assignPatientsByDistPoint(self):
        patient_list = self.patientListSorted()
        print('----------------')
        print(len(patient_list))
        print('----------------')
        self.total_capacity = 0

        for patient in patient_list:
            min_center = patient.temp_center
            if(patient.distance_to_Center(min_center)<25 and min_center.is_Full==False):
                min_center.addPatient(patient)
                self.assigned_patients += 1
        for center in self.centers:
            self.total_capacity += center.capacity
        if self.assigned_patients < self.total_capacity:
            self.assignbyDistPoint()

    def assignbyLostPoint(self):
        for center in self.centers:
            patient_list=self.lostPointList(center,25)
            range_s=min(int(center.capacity),len(patient_list)-1)
            for i in range(0,range_s):
                center.addPatient(patient_list[i])
                self.assigned_patients += 1

    def assignbyDistPoint(self):
        for center in self.centers:

            patient_list = self.distPointList(center, 25)

            range_s = min(int(center.capacity - len(center.patients)), len(patient_list))

            for i in range(0, range_s):
                if not patient_list[i].is_assigned :
                    center.addPatient(patient_list[i])
                    self.assigned_patients+=1

def simulated_annealing(network,initial_temperature,cooling_rate,epoch_length):
    T = initial_temperature
    incumbent_solution = copy.deepcopy(network)
    while T > 0.001:

        for epoch in range(1,epoch_length+1):

            # Pick 2 random centers
            center_1 = random.choice(network.centers)
            center_2 = random.choice(network.centers)
            while center_1 == center_2:
                center_2 = random.choice(network.centers)

            # Pick 2 random patients from these centers
            first_patient = random.choice(center_1.patients)
            second_patient = random.choice(center_2.patients)

            old_cost = center_1.distance_to_Patient(first_patient)*first_patient.np + center_2.distance_to_Patient(second_patient)*second_patient.np
            new_cost = center_1.distance_to_Patient(second_patient)*second_patient.np + center_2.distance_to_Patient(first_patient)*first_patient.np
            delta = new_cost - old_cost

            # If total distance reduces with this swap, Swap patients or accept according to metropolis criterion
            if delta < 0 or metropolis_criterion(delta,T): #
                center_1.remove_patient(first_patient)
                center_2.remove_patient(second_patient)
                center_2.addPatient(first_patient)
                center_1.addPatient(second_patient)

                #print(f"Temperature = {T:.3f}: Solution accepted with {delta}")

            else:
                pass
                #print(f"Temperature = {T:.3f} :Solution rejected with {delta}")

            if network.objective_function() < incumbent_solution.objective_function():
                incumbent_solution = copy.deepcopy(network)

        T *= cooling_rate

    return incumbent_solution

def metropolis_criterion(delta,T):
    random_number = random.random()
    criteria = math.exp(-delta/T)
    return random_number < criteria


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
    distance_centers=distanceMatrix.tail(distanceMatrix.shape[0] - patient_count)
    ch0_data = pd.read_excel('Capacity.xlsx',sheet_name='B3')
    center_index = 0

    for index, row in dialysis_centers.iterrows():
        ch0 = ch0_data['Orta'].iloc[center_index]
        current_center = Center(row['Merkez/Hastane No'],center_instance_no,row['Diyaliz merkezi'],row['İlçe'], row['Koordinat x_x'], row['Koordinat y_x'],  row['Makineler'],distance_centers.iloc[center_instance_no],patient_count,ch0=ch0)
        center_instance_no += 1
        network.add_center(current_center)
        center_index += 1

    network2 = copy.deepcopy(network)

    start = time.time()

    print('P2')
    network.assign_patients_balanced_sp()
    network.Print()

    end = time.time()
    print(f'P2 took {end-start}')

    print(20*"-")
    print('Simulated Annealing Approach')

    simulated_annealing_results = []

    for iteration in range(0,1):
        start = time.time()
        improved_network = copy.deepcopy(network)
        best_solution = simulated_annealing(network = improved_network,initial_temperature=1000,cooling_rate=0.99,epoch_length=3)
        improved_network.Print()
        end = time.time()
        simulated_annealing_results.append([iteration, best_solution.objective_function(),improved_network.objective_function(),end - start])

    simulated_annealing_result_df = pd.DataFrame(simulated_annealing_results,columns=['Run','Incumbent Objective Value','Final Objective Value','Runtime'])
    simulated_annealing_result_df.to_excel('Result.xlsx')
    print(simulated_annealing_result_df)


    l = list()
    network = Network(14,patient_count)
    center_instance_no = 0
    distance_centers = distanceMatrix.tail(distanceMatrix.shape[0] - patient_count)
    ch0_data = pd.read_excel('Capacity.xlsx', sheet_name='B3')
    center_index = 0
    for index, row in dialysis_centers.iterrows():
        for severity in ['İyimser', 'Orta', 'Karamsar']:
            ch0 = ch0_data[severity].iloc[center_index]
            current_center = Center(row['Merkez/Hastane No'],center_instance_no,row['Diyaliz merkezi'],row['İlçe'], row['Koordinat x_x'], row['Koordinat y_x'],  row['Makineler'],distance_centers.iloc[center_instance_no],patient_count,ch0=ch0)
            l.append([current_center.name, current_center.no, current_center.capacity, "B3",severity])
        center_index += 1

    df = pd.DataFrame(l, columns=["center name", "no", "capacity", "instance", 'Severity'])
    df.to_excel('kapasitelerB3.xlsx')
    y = 5