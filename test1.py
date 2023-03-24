a = [1,64,8,4,12,3,5,15,5]

def insertion_sort(points):
    for i in range(1, len(points)):
        key_item = points[i]
        j = i - 1
        while j >= 0 and points[j] > key_item:
            points[j + 1] = points[j]
            j -= 1
        points[j + 1] = key_item
    return 

insertion_sort(a)

print(a)

list1 = [1,2,2,3,3,4,5,6,7,8,9,10,5,7,20]
print("Original list : ",list1)


for ele in list1:
    if (ele%2) != 0:
        list1.remove(ele)

print("List after deleting all values which are odd : ",list1)