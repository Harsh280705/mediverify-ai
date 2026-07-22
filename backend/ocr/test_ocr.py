from pathlib import Path

from ocr.ocr_service import OCRService
from services.prescription_parser import PrescriptionParser


def print_bool(value):
    return "Yes" if value else "No"


def main():

    image_path = Path(r"D:\downloads\images.jpg")

    if not image_path.exists():
        print("Image not found!")
        return

    # OCR
    ocr = OCRService()

    # Parser
    parser = PrescriptionParser()

    # Extract OCR Text
    result = ocr.extract_text(str(image_path))

    print("\n" + "=" * 70)
    print("RAW OCR")
    print("=" * 70)
    print(result)

    # Parse
    prescription = parser.parse(result)

    print("\n" + "=" * 70)
    print("PRESCRIPTION DETAILS")
    print("=" * 70)

    print(f"Doctor       : {prescription['doctor'] or 'Not Found'}")
    print(f"Hospital     : {prescription['hospital'] or 'Not Found'}")
    print(f"Patient      : {prescription['patient_name'] or 'Not Found'}")
    print(f"Age          : {prescription['age'] or 'Not Found'}")
    print(f"Gender       : {prescription['gender'] or 'Not Found'}")
    print(f"Date         : {prescription['date'] or 'Not Found'}")
    print(f"Diagnosis    : {prescription['diagnosis'] or 'Not Found'}")
    print(f"Follow Up    : {prescription['follow_up'] or 'Not Found'}")

    print("\nAdvice")

    if prescription["advice"]:
        for advice in prescription["advice"]:
            print(f"• {advice}")
    else:
        print("Not Found")

    print("\n" + "=" * 70)
    print("MEDICINES")
    print("=" * 70)

    if not prescription["medicines"]:
        print("No medicines detected.")
        return

    for i, medicine in enumerate(prescription["medicines"], start=1):

        print(f"\nMedicine #{i}")
        print("-" * 50)

        print(f"OCR Name      : {medicine['ocr_name']}")

        if medicine["matched"]:
            best = medicine["matched"][0]

            print(f"Matched Name  : {best['generic']}")
            print(f"Brand         : {best['brand'] or 'N/A'}")
            print(f"Confidence    : {best['confidence']} %")
        else:
            print("Matched Name  : Not Found")
            print("Brand         : N/A")
            print("Confidence    : 0 %")

        print(f"Type          : {medicine['type'] or 'Unknown'}")
        print(f"Strength      : {medicine['strength'] or 'Not Found'}")

        schedule = medicine["schedule"]

        print("\nSchedule")
        print(f"Morning       : {print_bool(schedule['morning'])}")
        print(f"Afternoon     : {print_bool(schedule['afternoon'])}")
        print(f"Evening       : {print_bool(schedule['evening'])}")
        print(f"Night         : {print_bool(schedule['night'])}")

        print(f"\nMeal          : {medicine['meal'] or 'Not Found'}")
        print(f"Duration      : {medicine['duration_days'] or 'Not Found'} Days")


if __name__ == "__main__":
    main()