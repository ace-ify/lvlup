class ChocolateFactory {
    name;
    location;
    capacity;
    establishedYear;
    constructor(name, location, capacity, establishedYear) {
        this.name = name;
        this.location = location;
        this.capacity = capacity;
        this.establishedYear = establishedYear;
    }
}
// Example usage:
const wonkaFactory = new ChocolateFactory("Wonka's Chocolate Factory", "London", 10000, 1964);
console.log(wonkaFactory);
export {};
//# sourceMappingURL=scripts.js.map