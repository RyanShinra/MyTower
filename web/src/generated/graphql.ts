export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  Blocks: { input: number; output: number; }
  Meters: { input: number; output: number; }
  Pixels: { input: number; output: number; }
  Time: { input: number; output: number; }
};

export type AddElevatorBankInput = {
  readonly horizPosition: Scalars['Blocks']['input'];
  readonly maxFloor: Scalars['Int']['input'];
  readonly minFloor: Scalars['Int']['input'];
};

export type AddElevatorInput = {
  readonly elevatorBankId: Scalars['String']['input'];
};

export type AddFloorInput = {
  readonly floorType: FloorTypeGQL;
};

export type AddPersonInput = {
  readonly destFloor: Scalars['Int']['input'];
  readonly destHorizPosition: Scalars['Blocks']['input'];
  readonly initFloor: Scalars['Int']['input'];
  readonly initHorizPosition: Scalars['Blocks']['input'];
};

export type BuildingSnapshotGQL = {
  readonly __typename?: 'BuildingSnapshotGQL';
  readonly elevators: ReadonlyArray<ElevatorSnapshotGQL>;
  readonly elevatorBanks: ReadonlyArray<ElevatorBankSnapshotGQL>;
  readonly floors: ReadonlyArray<FloorSnapshotGQL>;
  readonly money: Scalars['Int']['output'];
  readonly people: ReadonlyArray<PersonSnapshotGQL>;
  readonly time: Scalars['Time']['output'];
};

export type ColorGQL = {
  readonly __typename?: 'ColorGQL';
  readonly alpha: Scalars['Int']['output'];
  readonly blue: Scalars['Int']['output'];
  readonly green: Scalars['Int']['output'];
  readonly red: Scalars['Int']['output'];
};

export type ElevatorBankSnapshotGQL = {
  readonly __typename?: 'ElevatorBankSnapshotGQL';
  readonly id: Scalars['String']['output'];
  readonly horizontalPosition: Scalars['Blocks']['output'];
  readonly minFloor: Scalars['Int']['output'];
  readonly maxFloor: Scalars['Int']['output'];
};

export type ElevatorSnapshotGQL = {
  readonly __typename?: 'ElevatorSnapshotGQL';
  readonly availableCapacity: Scalars['Int']['output'];
  readonly destinationFloor: Scalars['Int']['output'];
  readonly doorOpen: Scalars['Boolean']['output'];
  readonly horizontalPosition: Scalars['Blocks']['output'];
  readonly id: Scalars['String']['output'];
  readonly maxCapacity: Scalars['Int']['output'];
  readonly nominalDirection: VerticalDirectionGQL;
  readonly passengerCount: Scalars['Int']['output'];
  readonly state: ElevatorStateGQL;
  readonly verticalPosition: Scalars['Blocks']['output'];
  readonly verticalPositionMeters: Scalars['Meters']['output'];
  readonly verticalPositionPixels: Scalars['Pixels']['output'];
};

export type ElevatorStateGQL =
  | 'ARRIVED'
  | 'IDLE'
  | 'LOADING'
  | 'MOVING'
  | 'READY_TO_MOVE'
  | 'UNLOADING';

export type FloorSnapshotGQL = {
  readonly __typename?: 'FloorSnapshotGQL';
  readonly floorColor: ColorGQL;
  readonly floorHeight: Scalars['Blocks']['output'];
  readonly floorHeightMeters: Scalars['Meters']['output'];
  readonly floorNumber: Scalars['Int']['output'];
  readonly floorType: FloorTypeGQL;
  readonly floorWidth: Scalars['Blocks']['output'];
  readonly floorboardColor: ColorGQL;
  readonly leftEdgeBlock: Scalars['Blocks']['output'];
  readonly personCount: Scalars['Int']['output'];
};

export type FloorTypeGQL =
  | 'APARTMENT'
  | 'HOTEL'
  | 'LOBBY'
  | 'OFFICE'
  | 'RESTAURANT'
  | 'RETAIL';

export type Mutation = {
  readonly __typename?: 'Mutation';
  readonly addElevator: Scalars['String']['output'];
  readonly addElevatorBank: Scalars['String']['output'];
  readonly addElevatorBankSync: Scalars['String']['output'];
  readonly addElevatorSync: Scalars['String']['output'];
  readonly addFloor: Scalars['String']['output'];
  readonly addFloorSync: Scalars['Int']['output'];
  readonly addPerson: Scalars['String']['output'];
  readonly addPersonSync: Scalars['String']['output'];
};


export type MutationaddElevatorArgs = {
  input: AddElevatorInput;
};


export type MutationaddElevatorBankArgs = {
  input: AddElevatorBankInput;
};


export type MutationaddElevatorBankSyncArgs = {
  input: AddElevatorBankInput;
};


export type MutationaddElevatorSyncArgs = {
  input: AddElevatorInput;
};


export type MutationaddFloorArgs = {
  input: AddFloorInput;
};


export type MutationaddFloorSyncArgs = {
  input: AddFloorInput;
};


export type MutationaddPersonArgs = {
  input: AddPersonInput;
};


export type MutationaddPersonSyncArgs = {
  input: AddPersonInput;
};

export type PersonSnapshotGQL = {
  readonly __typename?: 'PersonSnapshotGQL';
  readonly DrawColor: ReadonlyArray<Scalars['Int']['output']>;
  readonly currentFloorNum: Scalars['Int']['output'];
  readonly currentHorizontalPosition: Scalars['Blocks']['output'];
  readonly currentVerticalPosition: Scalars['Blocks']['output'];
  readonly destinationFloorNum: Scalars['Int']['output'];
  readonly destinationHorizontalPosition: Scalars['Blocks']['output'];
  readonly drawColor: ColorGQL;
  readonly madFraction: Scalars['Float']['output'];
  readonly personId: Scalars['String']['output'];
  readonly state: PersonStateGQL;
  readonly waitingTime: Scalars['Time']['output'];
};

export type PersonStateGQL =
  | 'IDLE'
  | 'IN_ELEVATOR'
  | 'WAITING_FOR_ELEVATOR'
  | 'WALKING';

export type Query = {
  readonly __typename?: 'Query';
  readonly allPeople?: Maybe<ReadonlyArray<PersonSnapshotGQL>>;
  readonly buildingState?: Maybe<BuildingSnapshotGQL>;
  readonly gameTime: Scalars['Time']['output'];
  readonly hello: Scalars['String']['output'];
  readonly isRunning: Scalars['Boolean']['output'];
};

export type Subscription = {
  readonly __typename?: 'Subscription';
  readonly buildingStateStream?: Maybe<BuildingSnapshotGQL>;
  readonly gameTimeStream: Scalars['Time']['output'];
};


export type SubscriptionbuildingStateStreamArgs = {
  intervalMs?: Scalars['Int']['input'];
};


export type SubscriptiongameTimeStreamArgs = {
  intervalMs?: Scalars['Int']['input'];
};

export type VerticalDirectionGQL =
  | 'DOWN'
  | 'STATIONARY'
  | 'UP';
